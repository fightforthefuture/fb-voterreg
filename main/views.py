import facebook
import urllib
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from tasks import fetch_fb_friends, update_friends_of
from decorators import render_json
from voterapi import fetch_voter_from_fb_profile, correct_voter
from models import User, FriendshipBatch, BATCH_REGULAR
from datetime import datetime
from fb_utils import FacebookProfile


class SafariView(TemplateView):
    template_name = 'safari.html'


def _post_index(request):
    signed_request = request.POST["signed_request"]
    data = facebook.parse_signed_request(
        signed_request,
        settings.FACEBOOK_APP_SECRET)
    if not data.get("user_id") or not hasattr(request, 'facebook'):
        scope = ["user_birthday", "user_location", "friends_birthday,"
                 "friends_hometown", "friends_location", "email"]
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
    if user.friends_need_fetching():
        user.update_friends_fetch()
        user.save()
        fetch_fb_friends.delay(fb_uid, access_token)


@csrf_exempt
def index(request):
    if request.method == "POST":
        if request.GET.get("source", False):
            request.session["source"] = request.GET["source"]
            request.session.modified = True
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
        fb_profile = graph.get_object("me")
        profile = FacebookProfile(fb_profile)
        voter = fetch_voter_from_fb_profile(profile)
        user.name = fb_profile["name"]
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.email = fb_profile.get("email", "")
        user.birthday = profile.dob
        user.location_name = profile.location or ""
        user.location_state = profile.location_state or ""
        user.location_city = profile.location_city or ""
        user.far_from_home = profile.far_from_home()
        if voter:
            user.votizen_id = voter.id
            user.registered = voter.registered
        user.data_fetched = True
        user.save()
        if user.registered:
            update_friends_of.delay(
                user.id, request.facebook["access_token"])
    redirect_url = reverse("main:pledge") if user.registered \
        else reverse("main:register")
    return HttpResponse(redirect_url, content_type="text/plain")


def _friend_listing_page(request, template, additional_context={}, user=None):
    if not user:
        user = User.objects.get(fb_uid=request.facebook["uid"])
    context = {"user": user}
    context.update(additional_context)
    if user.friendship_set.filter(registered=True).count() >= 4:
        context["friends"] = user.friendship_set.order_by("-display_ordering")[:4]
    else:
        _fetch_fb_friends(request)
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request))


def register(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    context = {
        "name": user.name,
        "page": "register"
    }
    if user.location_city:
        context["location"] = "{0}, {1}".format(
            user.location_city, user.location_state)
    if user.birthday:
        context["birthday"] = user.birthday.strftime("%b %d, %Y")
    return _friend_listing_page(
        request, "register.html", additional_context=context, user=user)


def pledge(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if request.GET.get("from_widget", False):
        user.registered = True
        user.used_registration_widget = True
        user.save()
        update_friends_of.delay(
            user.id, request.facebook["access_token"])
        messages.add_message(
            request, messages.INFO,
            "Thank you for registering to vote!")
    return _friend_listing_page(
        request, "pledge.html",
        additional_context={"page": "pledge"})


def invite_friends(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_mgr = user.friendship_set
    context = {
        "page": "friends",
        "num_registered": f_mgr.filter(registered=True).count(),
        "num_pledged": f_mgr.filter(date_pledged__isnull=False).count(),
        "num_friends": user.num_friends,
        "uninvited_batches": user.friendshipbatch_set.filter(
            completely_fetched=True, invite_date__isnull=True),
        "still_loading": not user.friends_fetched,
        "my_city": user.location_city}
    return render_to_response(
        "invite_friends.html",
        context,
        context_instance=RequestContext(request))


@render_json
def submit_pledge(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.date_pledged = datetime.now()
    user.save()
    update_friends_of.delay(
        user.id, request.facebook["access_token"])
    messages.add_message(
        request, messages.INFO,
        "Thank you for pledging to vote!")
    return {"next": reverse("main:invite_friends")}


@render_json
def fetch_friends(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if user.friendship_set.filter(registered=True).count() < 4:
        return {"fetched": False}
    friends = user.friendship_set.order_by("-display_ordering")[:4]
    html = render_to_string(
        "_friends.html",
        {"friends": friends},
        context_instance=RequestContext(request))
    return {"fetched": True,
             "html": html}


@render_json
def wont_vote(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.wont_vote_reason = "rather_not_say"
    user.save()
    messages.add_message(
        request, messages.INFO,
        "Thank you! Even though you can't vote, you can still invite your friends.")
    return {"next": reverse("main:invite_friends")}


@render_json
def im_actually_registered(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.registered = True
    user.save()
    correct_voter(user.fb_uid)
    messages.add_message(
        request, messages.INFO,
        "You're now marked as registered to vote.")
    return {"next": reverse("main:pledge")}


@render_json
def fetch_updated_batches(request):
    _fetch_fb_friends(request)
    batch_ids = request.GET["batchids"]
    if batch_ids == "":
        batch_ids = []
    else:
        batch_ids = set([int(b) for b in batch_ids.split(",")])
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_mgr = user.friendship_set
    batches = user.friendshipbatch_set.filter(
        completely_fetched=True, invite_date__isnull=True)
    htmls = []
    for batch in batches:
        if batch.id not in batch_ids:
            htmls.append(
                render_to_string(
                    "_batch.html", {"batch": batch},
                    context_instance=RequestContext(request)))
    return {
        "num_registered": f_mgr.filter(registered=True).count(),
        "num_pledged": f_mgr.filter(date_pledged__isnull=False).count(),
        "num_friends": user.num_friends or 0,
        "num_processed": f_mgr.all().count(),
        "boxes": htmls,
        "finished": user.friends_fetched}


@render_json
def mark_batch_invited(request):
    batch_id = int(request.GET["batch_id"])
    batch = FriendshipBatch.objects.get(id=batch_id)
    batch.invite_date = datetime.now()
    batch.save()
    return {"response": "ok"}


def unregistered_friends_list(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    batches = user.friendshipbatch_set.filter(
        completely_fetched=True, type=BATCH_REGULAR)
    friendships = []
    for batch in batches:
        friendships.extend(list(batch.friendship_set.all()))
    return render_to_response(
        "unregistered_friends_list.html",
        {"friendships": friendships},
        context_instance=RequestContext(request))


def register_widget(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    widget_qs = {
        "first_name": user.first_name,
        "last_name": user.last_name}
    if user.email:
        widget_qs["email"] = user.email
    if user.location_city:
        widget_qs["city"] = user.location_city
        widget_qs["state"] = user.location_state
    if user.birthday:
        widget_qs["dob_month"] = user.birthday.month
        widget_qs["dob_day"] = user.birthday.day
        widget_qs["dob_year"] = user.birthday.year
    return render_to_response(
        "register_widget.html",
        {"widget_qs": urllib.urlencode(widget_qs),
          "page": "register"},
        context_instance=RequestContext(request))
