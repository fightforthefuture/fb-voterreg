from django.conf import settings

def add_settings(request):
    return { "FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID,
             "BASE_URL": settings.BASE_URL }
