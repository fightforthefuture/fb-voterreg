import facebook
from django.conf import settings
from main.models import User
from datetime import date

def add_settings(request):
    return { "FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID,
             "BASE_URL": settings.BASE_URL,
             "KM_CODE": settings.KM_CODE,
             "FACEBOOK_CANVAS_PAGE": settings.FACEBOOK_CANVAS_PAGE,
             "DEBUG_APP_REQUESTS": settings.DEBUG_APP_REQUESTS,
             "INSTALLATION": settings.INSTALLATION }

def add_days_left(request):
    return { "num_days_left": (date(2012, 11, 6) - date.today()).days }

def add_fbuid(request):
    if hasattr(request, "facebook") and request.facebook is not None:
        return { "my_uid": request.facebook["uid"] }
    else:
        return {}

def add_source(request):
    if request.GET.get("source", False):
        return { "traffic_source": request.GET["source"] }
    else:
        return {}

def fb_user(request):
    """
    Makes FQL query to add data from the authenticated user's row in the user
    table, making it available in all templates under the fb_user namespace.

    Retrieves all fields defined in the `fields` list. For a full list of
    available fields, see the user table reference:

    https://developers.facebook.com/docs/reference/fql/user/
    """
    try:
        api = facebook.GraphAPI(request.facebook['access_token'])
        fields = [
            'pic',
            'first_name',
            'last_name',
        ]
        data = api.fql('SELECT %s FROM user WHERE uid=me()' % ', '.join(fields))
        return {
            'fb_user': data[0]
        }
    except (TypeError, facebook.GraphAPIError,):
        return {}


def vwf_user(request):
    """
    User
    """
    try:
        return {
            'vwf_user': User.objects.get(fb_uid=request.facebook['uid'])
        }
    except TypeError:
        return {}


def urls(request):
    return {
        'base_url': settings.BASE_URL,
        'sharing_url': settings.SHARING_URL,
    }
