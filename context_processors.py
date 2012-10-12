from django.conf import settings

def add_settings(request):
    return { "FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID,
             "BASE_URL": settings.BASE_URL,
             "KM_CODE": settings.KM_CODE,
             "FACEBOOK_CANVAS_PAGE": settings.FACEBOOK_CANVAS_PAGE,
             "DEBUG_APP_REQUESTS": settings.DEBUG_APP_REQUESTS }

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
