import facebook
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
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
        if request.POST.get("safari", False):
            fb_user = { "method": "safari",
                        "uid": request.POST["uid"],
                        "access_token": request.POST["access_token"] }
            return fb_user
        fb_user = self._get_fb_user_cookie(request)
        if fb_user:
            return fb_user
        return self._get_fb_user_canvas(request)

    def _is_initial_safari_post(self, request):
        if 'fb_user' not in request.session and \
                'safari' not in request.POST:
            ua = request.META['HTTP_USER_AGENT']
            if 'Safari' in ua and not 'Chrome' in ua:
                return True
        return False

    def process_request(self, request):
        fb_user = self._get_fb_user(request)
        request.facebook = fb_user
        if fb_user:
            user, created = User.objects.get_or_create(fb_uid=fb_user["uid"])
            # Safari blocks third-party cookies by default.
            if self._is_initial_safari_post(request):
                return render_to_response(
                    'safari.html', 
                    { 'fb_uid': fb_user['uid'],
                      'signed_request': request.POST['signed_request'],
                      'access_token': fb_user['access_token']}, 
                    RequestContext(request))
            request.session["fb_user"] = fb_user
            request.session.modified = True

        request.facebook = request.session.get("fb_user", None)

        return None
