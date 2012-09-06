import facebook
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import voting_api
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

def _friends_context(request, user):
    return 

@csrf_exempt
def index(request):
    user, created = User.objects.get_or_create(fb_uid=request.facebook["uid"])
    context = {}
    if user.data_fetched or voting_api.requests_exhausted():
        context["fetched"] = True
        context["registered"] = user.registered
        context["pledged"] = user.pledged
        context["invited_friends"] = user.invited_friends
        if user.friends_fetched:
            context["friends"] = \
                user.friends_set.order_by("-display_ordering")[:4]
    else:
        context["fetched"] = False
    return render_to_response(
        "main_index.html", 
        context, 
        RequestContext(request))
