from django.conf import settings

def add_settings(request):
    return { "FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID,
             "BASE_URL": settings.BASE_URL,
             "KM_CODE": settings.KM_CODE }
