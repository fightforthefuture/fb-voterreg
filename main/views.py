import facebook
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from tasks import fetch_fb_friends
from decorators import render_json
from voterapi import fetch_voter_from_fb_profile
from models import User

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

@csrf_exempt
def index(request):
    if request.method == "POST":
        response = _post_index(request)
        if response:
            return response
    user = User.objects.get(fb_uid=request.facebook["uid"])
    context = {}
    if user.data_fetched:
        context["fetched"] = True
        context.update(_main_content_context(user))
        if user.friends_fetched:
            context["friends"] = \
                user.friends.order_by("-display_ordering")[:4]
    else:
        context["fetched"] = False
    if not user.friends_fetched:
        fetch_fb_friends.delay(request.facebook["uid"],
                               request.facebook["access_token"])
    return render_to_response(
        "main_index.html", 
        context, 
        RequestContext(request))

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
    return render_to_response(
        "_main_content.html",
        _main_content_context(user),
        RequestContext(request))

@render_json
def fetch_friends(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if not user.friends_fetched:
        return { "fetched": False }
    friends = user.friends.order_by("-display_ordering")[:4]
    html = render_to_string(
        "_main_friends.html",
        { "friends": friends },
        context_instance=RequestContext(request))
    return { "fetched": True,
             "html": html }

def register(request):
    return None
