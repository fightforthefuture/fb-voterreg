import facebook
from django.conf import settings
from django.shortcuts import redirect
from main.models import User

class FacebookMiddleware(object):
    def _get_fb_user_cookie(self, request):
        fb_user = facebook.get_user_from_cookie(request.COOKIES,
            settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
        if fb_user:
            fb_user['method'] = 'cookie'
        return fb_user

    def _get_fb_user_canvas(self, request):
        fb_user = None
        if request.POST.get('signed_request'):
            signed_request = request.POST["signed_request"]
            data = facebook.parse_signed_request(
                signed_request,
                settings.FACEBOOK_APP_SECRET)
            if data and data.get('user_id'):
                fb_user = data['user']
                fb_user['method'] = 'canvas'
                fb_user['uid'] = data['user_id']
                fb_user['access_token'] = data['oauth_token']
        return fb_user

    def _get_fb_user(self, request):
        fb_user = self._get_fb_user_cookie(request)
        if fb_user:
            return fb_user
        return self._get_fb_user_canvas(request)

    def process_request(self, request):
        fb_user = self._get_fb_user(request)
        request.facebook = fb_user
        if fb_user:
            user, created = User.objects.get_or_create(fb_uid=fb_user["uid"])
            request.session["fb_user"] = fb_user
            request.session.modified = True
        else:
            request.facebook = request.session.get("fb_user", None)

        # Safari blocks third-party cookies by default.
        ua = request.META['HTTP_USER_AGENT']
        is_safari = 'Safari' in ua and not 'Chrome' in ua
        if 'uid' not in request.facebook and is_safari:
            return redirect("main:safari")

        return None
