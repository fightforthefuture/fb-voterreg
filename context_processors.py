from django.conf import settings

def add_settings(request):
    return { "FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID,
             "BASE_URL": settings.BASE_URL,
             "KM_CODE": settings.KM_CODE }

def add_fbuid(request):
    if hasattr(request, "facebook") and request.facebook is not None:
        return { "my_uid": request.facebook["uid"] }
    else:
        return {}

def add_source(request):
    if request.session.get("source", False):
        source = request.session["source"]
        del request.session["source"]
        request.session.modified = True
        return { "traffic_source": source }
    else:
        return {}
