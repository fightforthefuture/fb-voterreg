from django.conf import settings

def add_fb_info(request):
    return { "FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID }
