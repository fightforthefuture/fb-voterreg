import facebook
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from fb_friends import get_friends
from tasks import fetch_fb_friends, update_friends_of
from decorators import render_json
from voterapi import fetch_voter_from_fb_profile, correct_voter
from models import User
from forms import WontVoteForm
from datetime import datetime

def _post_index(request):
    signed_request = request.POST["signed_request"]
    data = facebook.parse_signed_request(
        signed_request,
        settings.FACEBOOK_APP_SECRET)
    if not data.get("user_id"):
        scope = ["user_birthday", "user_location", "friends_birthday,"
                 "friends_hometown", "friends_location"]
        auth_url = facebook.auth_url(settings.FACEBOOK_APP_ID,
                                     settings.FACEBOOK_CANVAS_PAGE,
                                     scope)
        markup = ('<script type="text/javascript">'
                  'top.location.href="%s"</script>' % auth_url)
        return HttpResponse(markup)
    return None

def _main_content_context(user):
    return {
        "registered": user.registered,
        "pledged": user.pledged,
        "invited_friends": user.invited_friends
    }

def _index_redirect(user):
    if user.wont_vote:
        return redirect("main:invite_friends")
    elif user.registered:
        if user.pledged:
            return redirect("main:invite_friends")
        else:
            return redirect("main:pledge")
    else:
        return redirect("main:register")

def _fetch_fb_friends(request):
    fb_uid = request.facebook["uid"]
    access_token = request.facebook["access_token"]
    user = User.objects.get(fb_uid=fb_uid)
    if not user.friends_fetch_started:
        fetch_fb_friends.delay(fb_uid, access_token)
        user.friends_fetch_started = True
        user.save()

@csrf_exempt
def index(request):
    if request.method == "POST":
        response = _post_index(request)
        if response:
            return response
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if user.data_fetched:
        return _index_redirect(user)
    return render_to_response(
        "loading.html", 
        context_instance=RequestContext(request))

def fetch_me(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if not user.data_fetched:
        graph = facebook.GraphAPI(request.facebook["access_token"])
        profile = graph.get_object("me")
        voter = fetch_voter_from_fb_profile(profile)
        # possibly save other data here in future, e.g. years voted
        # in past
        user.name = profile["name"]
        user.data_fetched = True
        if voter:
            user.votizen_id = voter.id
            user.registered = voter.registered
        user.save()
        if user.registered:
            update_friends_of.delay(
                user.id, request.facebook["access_token"])
    redirect_url = reverse("main:pledge") if user.registered \
        else reverse("main:register")
    return HttpResponse(redirect_url, content_type="text/plain")

def _friend_listing_page(request, template, additional_context={}):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    context = { "user": user }
    context.update(additional_context)
    if user.friends_fetched:
        context["friends"] = user.friendship_set.order_by("-display_ordering")[:4]
    else:
        _fetch_fb_friends(request)
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request))

def register(request):
    return _friend_listing_page(
        request, "register.html", 
        { "wont_vote_form": WontVoteForm() })

def pledge(request):
    return _friend_listing_page(request, "pledge.html")

def invite_friends(request):
    return _friend_listing_page(request, "invite_friends.html")

@render_json
def submit_pledge(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.date_pledged = datetime.now()
    user.save()
    return { "response": "ok" }

@render_json
def fetch_friends(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if not user.friends_fetched:
        return { "fetched": False }
    friends = user.friendship_set.order_by("-display_ordering")[:4]
    html = render_to_string(
        "_friends.html",
        { "friends": friends },
        context_instance=RequestContext(request))
    return { "fetched": True,
             "html": html }

def friend_invite_list(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    dont_invite_list = set([f.fb_uid for f in user.friendship_set.all()
                            if not f.needs_invitation()])
    # fb lets you send requests to a max of 50 users.
    fb_friends = get_friends(request.facebook["access_token"], 50)
    fb_uids = [f["id"] for f in fb_friends if f["id"] not in dont_invite_list]
    return HttpResponse(",".join(fb_uids), content_type="text/plain")

def wont_vote(request):
    form = WontVoteForm(request.POST)
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if form.is_valid():
        user.wont_vote_reason = form.cleaned_data["wont_vote_reason"]
        user.save()
        return redirect("main:invite_friends")

@render_json
def im_actually_registered(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.registered = True
    user.save()
    correct_voter(user.fb_uid)
    return { "next": reverse("main:pledge") }

def register_widget(request):
    return render_to_response(
        "register_widget.html",
        context_instance=RequestContext(request))
