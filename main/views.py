import facebook
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

def _post_index(request):
    signed_request = request.POST["signed_request"]
    data = facebook.parse_signed_request(
        signed_request,
        settings.FACEBOOK_SECRET_KEY)
    if not data.get("user_id"):
        scope = ("user_birthday,user_location,friends_birthday,"
                 "friends_hometown,friends_location")
        auth_url = facebook.auth_url(settings.FACEBOOK_APP_ID,
                                     settings.FACEBOOK_CANVAS_PAGE,
                                     scope)
        markup = ('<script type="text/javascript">'
                  'top.location.href="%s"</script>' % auth_url)
        return HttpResponse(markup)
    return None

@csrf_exempt
def index(request):
    if request.method == "POST":
        response = _post_index(request)
        if response:
            return response
    return render_to_response("main_index.html", { }, RequestContext(request))
