import facebook
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib import messages
from main.models import User, BADGE_INVITED, BADGE_PLEDGED
import urllib
from urllib2 import quote


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
        if request.GET.get("no_cookies", False):
            fb_user = { "method": "no_cookies",
                        "uid": request.GET["fb_uid"],
                        "access_token": request.GET["access_token"] }
            return fb_user
        fb_user = self._get_fb_user_cookie(request)
        if fb_user:
            return fb_user
        return self._get_fb_user_canvas(request)

    def _is_initial_request(self, request):
        return 'fb_user' not in request.session and \
            'no_cookies' not in request.POST and \
            'no_cookies' not in request.GET

    def _unsubscribe_response(self):
        return HttpResponse('<script>top.location.href="{0}/nowunsubscribed";</script>'.format(settings.BASE_URL))

    def process_request(self, request):
        if request.path.startswith("/unsubscribe"):
            return self._unsubscribe_response()
        fb_user = self._get_fb_user(request)
        request.facebook = fb_user
        if fb_user:
            user, created = User.objects.get_or_create(fb_uid=fb_user["uid"])
            # Some browsers block third-party cookies by default.
            if self._is_initial_request(request):
                inner_query_string = request.META["QUERY_STRING"]
                request.session["fb_user"] = fb_user
                request.session.modified = True
                query_string_params = {}
                for k, v in request.GET.items():
                    query_string_params[k] = v
                query_string_params.update({ 
                        'fb_uid': fb_user['uid'],
                        'signed_request': request.POST['signed_request'],
                        'access_token': fb_user['access_token'],
                        'no_cookies': True })
                query_string = urllib.urlencode(query_string_params)
                return render_to_response(
                    'cookies_test.html', 
                    { 'query_string': query_string,
                      'inner_query_string': inner_query_string }, 
                    RequestContext(request))
            request.session["fb_user"] = fb_user
            request.session.modified = True
        request.facebook = request.session.get("fb_user", None)
        return None


    def process_exception(self, request, exception):
        """
        Intercepts any GraphAPIError exceptions, which are almost always thrown
        to an expired session key. Per Facebook's recommendation [1], we use a
        JavaScript redirect in the response to send them back for
        reauthorization and a new access token.

        [1] https://developers.facebook.com/blog/post/2011/05/13/how-to--handle-expired-access-tokens/
        """
        if issubclass(exception.__class__, facebook.GraphAPIError):
            reauth_url = 'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s' % (
                quote(settings.FACEBOOK_APP_ID),
                quote(settings.FACEBOOK_CANVAS_PAGE + '?target=' + request.path),
            )
            return HttpResponse(
                '<script>top.location.href="%s";</script>' % reauth_url
            )

        return None

    def process_response(self, request, response):
        # for MSIE 9 and 10.
        response['P3P'] = 'CP="IDC CURa ADMa OUR IND PHY ONL COM STA"'
        return response


class BadgeMiddleware(object):
    def process_request(self, request):
        if not request.facebook:
            return None
        try:
            user = User.objects.get(fb_uid=request.facebook['uid'])
        except User.DoesNotExist:
            return None
        won_badges = user.wonbadge_set.filter(num__gt=0, message_shown=False)
        if len(won_badges) > 0:
            won_badge = won_badges[0]
            if won_badge.badge_type == BADGE_INVITED:
                verb = "invited"
            elif won_badge.badge_type == BADGE_PLEDGED:
                verb = "pledged"
            else:
                verb = "voted"
            messages.add_message(
                request, messages.INFO,
                "<div class=\"with-badges\"><span class=\"badge\">{0}</span> {0} friends {1}! You just earned a badge.</div>".format(
                    won_badge.num, verb))
            user.wonbadge_set.all().update(message_shown=True)
        return None


class UAMiddleware(object):
    """
    Intercepts requests from user agents known to be unsupported, returning
    them a message explaining that we do not support their browser and
    proposing a course of action.
    """
    def process_request(self, request):
        ua_string = request.META['HTTP_USER_AGENT']
        bad_agents = [
            'MSIE 6.',
            'MSIE 7.',
            'MSIE 8.',
        ]
        if any(agent in ua_string for agent in bad_agents):
            return HttpResponse(render_to_string('unsupported_ua.html'))
        return None
