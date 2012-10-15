import facebook
import requests
import urllib
import sys
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotAllowed
from tasks import fetch_fb_friends, update_friends_of
from decorators import render_json
from voterapi import fetch_voter_from_fb_profile, correct_voter
from models import User, FriendshipBatch, BATCH_REGULAR
from datetime import datetime, date
from fb_utils import FacebookProfile
from django.core.mail import EmailMultiAlternatives
from models import BATCH_BARELY_LEGAL
import logging


class SafariView(TemplateView):
    template_name = 'safari.html'


class OGObjectView(TemplateView):
    """
    The view used to serve the OpenGraph objects published whenever a user
    pledges to vote.
    """
    template_name = 'pledge/index.html'

    def get_context_data(self, **kwargs):
        context = super(OGObjectView, self).get_context_data(**kwargs)
        context['base_url'] = settings.BASE_URL
        context['canvas_url'] = settings.FACEBOOK_CANVAS_PAGE
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID
        return context


def _post_index(request):
    query_string = request.META["QUERY_STRING"]
    redirect_uri = settings.FACEBOOK_CANVAS_PAGE
    if query_string:
        redirect_uri += ("?" + query_string)
    signed_request = request.POST["signed_request"]
    data = facebook.parse_signed_request(
        signed_request,
        settings.FACEBOOK_APP_SECRET)
    if not data.get("user_id"):
        scope = ["user_birthday", "user_location", "friends_birthday,"
                 "friends_hometown", "friends_location", "email",
                 "publish_actions"]
        auth_url = facebook.auth_url(settings.FACEBOOK_APP_ID,
                                     redirect_uri, scope)
        markup = ('<script type="text/javascript">'
                  'top.location.href="%s"</script>' % auth_url)
        return HttpResponse(markup)
    return None


def _main_content_context(user):
    return {
        "registered": user.registered,
        "pledged": user.pledged,
        "invited_friends": user.invited_friends
    }


def _index_redirect(user, query_string=""):
    if query_string:
        query_string = "?" + query_string
    if user.wont_vote:
        return redirect(reverse("main:invite_friends_2") + query_string)
    else:
        return redirect(reverse("main:my_vote") + query_string)


def _fetch_fb_friends(request):
    fb_uid = request.facebook["uid"]
    access_token = request.facebook["access_token"]
    user = User.objects.get(fb_uid=fb_uid)
    if user.friends_need_fetching():
        user.update_friends_fetch()
        user.save()
        fetch_fb_friends.delay(fb_uid, access_token)


def _unpledge(request):
    if request.method == 'POST':
        user = User.objects.get(fb_uid=request.facebook["uid"])
        user.date_pledged = None
        user.save()
        update_friends_of.delay(
            user.id, request.facebook["access_token"])
        messages.add_message(
            request, messages.INFO,
            # Translators: message displayed to users when they unpledge
            _("Sorry to hear that you're no longer pledging to vote.")
        )
        return redirect('main:my_vote')
    return HttpResponseNotAllowed()


@csrf_exempt
def index(request):
    if request.method == "POST":
        response = _post_index(request)
        if response:
            return response
    user = User.objects.get(fb_uid=request.facebook["uid"])
    query_string = request.META["QUERY_STRING"]
    if user.data_fetched:
        target_url = request.GET.get("target", None)
        if target_url:
            return redirect(target_url)
        else:
            return _index_redirect(user, query_string)
    return render_to_response(
        "loading.html",
        context_instance=RequestContext(request))


def my_vote(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if user.pledged and user.registered:
        return redirect('main:my_vote_vote')
    elif user.registered:
        return redirect('main:my_vote_pledge')
    else:
        return redirect('main:my_vote_register')


def my_vote_register(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    context = {
        "page": "register"
    }
    if user.location_city:
        context["location"] = "{0}, {1}".format(
            user.location_city, user.location_state)
    if user.birthday:
        context["birthday"] = user.birthday.strftime("%b %d, %Y")
    return _friend_listing_page(
        request, "my_vote_register.html", additional_context={
        'page': 'my_vote',
        'section': 'register',
        'user': user,
        "name": user.name,
    }, user=user)


def my_vote_pledge(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if request.GET.get("from_widget", False):
        user.registered = True
        user.used_registration_widget = True
        user.save()
        update_friends_of.delay(
            user.id, request.facebook["access_token"])
        messages.add_message(
            request, messages.INFO,
            # Translators: message displayed to users in green bar when they register to vote
            _("Thank you for registering to vote!")
        )
    return render_to_response("my_vote_pledge.html", {
        'page': 'my_vote',
        'section': 'pledge',
        'user': user,
    }, context_instance=RequestContext(request))


def my_vote_vote(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])

    if request.method == 'GET':
        return render_to_response("my_vote_vote.html", {
            'page': 'my_vote',
            'section': 'vote',
            'user': user,
        }, context_instance=RequestContext(request))

    elif request.method == 'POST':
        explicit_share = request.POST.get('tell-friends', '') == 'on'
        #if explicit_share:
        #    requests.post(settings.FACEBOOK_OG_PLEDGE_URL, params={
        #        'website': settings.BASE_URL + reverse('pledge_object'),
        #        'access_token': request.facebook['access_token'],
        #        'fb:explicitly_shared': 'true',
        #    })
        user.explicit_share_vote = explicit_share

        if 'yes' in request.POST:
            user.date_voted = datetime.now()
            messages.add_message(
                request, messages.INFO,
                # Translators: message displayed to users in when they mark themselves as having voted.
                _("Your voice was heard! Make sure your friends' voices are also heard:")
            )
            redirect_view = 'main:invite_friends_2'
        else:
            user.date_voted = None
            messages.add_message(
                request, messages.INFO,
                # Translators: message displayed to users in when they mark themselves as not having voted.
                _("Got it, you haven't voted yet. Don't forget!")
            )
            redirect_view = 'main:my_vote_vote'
        user.save()

        update_friends_of.delay(
            user.id, request.facebook["access_token"])

        return redirect(redirect_view)


def fetch_me(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if not user.data_fetched:
        graph = facebook.GraphAPI(request.facebook["access_token"])
        fb_profile = graph.get_object("me")
        profile = FacebookProfile(fb_profile)
        voter = fetch_voter_from_fb_profile(profile)
        user.name = fb_profile["name"]
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.email = fb_profile.get("email", "")
        user.birthday = profile.dob
        user.location_name = profile.location or ""
        user.location_state = profile.location_state or ""
        user.location_city = profile.location_city or ""
        user.far_from_home = profile.far_from_home()
        if voter:
            user.votizen_id = voter.id
            user.registered = voter.registered
        user.data_fetched = True
        user.save()
        try:
            _send_join_email(user, request)
        except Exception as e:
            logging.exception("error sending join email")
        if user.registered:
            update_friends_of.delay(
                user.id, request.facebook["access_token"])
    redirect_url = reverse("main:pledge") if user.registered \
        else reverse("main:register")
    return HttpResponse(redirect_url, content_type="text/plain")

def _send_join_email(user, request):
    today = date.today()
    num_days = (date(2012, 11, 6) - today).days
    invite_friends_url = reverse('main:invite_friends')
    unsubscribe_url = reverse('main:unsubscribe')
    html_body = render_to_string(
        "join_email.html",
        {
            "num_days": num_days,
            "invite_friends_url": invite_friends_url,
            "unsubscribe_url": unsubscribe_url,
        },
        context_instance=RequestContext(request))
    text_body = render_to_string(
        "join_email.txt",
        {
            "num_days": num_days,
            "invite_friends_url": invite_friends_url,
            "unsubscribe_url": unsubscribe_url,
        },
        context_instance=RequestContext(request))
    if user.email:
        msg = EmailMultiAlternatives(
            # Translators: subject of email sent to users when they join the app
            _("Re: Vote with Friends"),
            text_body,
            settings.EMAIL_SENDER,
            [user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)

def _friend_listing_page(request, template, additional_context={}, user=None):
    if not user:
        user = User.objects.get(fb_uid=request.facebook["uid"])
    context = {"user": user}
    context.update(additional_context)
    if user.friendship_set.filter(registered=True).count() >= 4:
        context["friends"] = user.friendship_set.order_by("-display_ordering")[:4]
    else:
        _fetch_fb_friends(request)
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request))


def register(request):
    return redirect('main:my_vote_register')


def pledge(request):
    return redirect('main:my_vote_pledge')


def _invite_friends_2_qs(user, section, start_index=0):
    f_qs = user.friendship_set.all()
    if section == "invited":
        f_qs = f_qs.filter(
            Q(invited_with_batch=True) | Q(invited_individually=True))
    elif section == "not_invited":
        f_qs = f_qs.filter(
            invited_with_batch=False, 
            invited_individually=False, 
            date_pledged__isnull=True)
    elif section == "pledged":
        f_qs = f_qs.filter(date_pledged__isnull=False)
    elif section == "registered":
        f_qs = f_qs.filter(registered=True)
    elif section == "voted":
        f_qs = f_qs.filter(date_voted__isnull=False)
    return f_qs.order_by("fb_uid")[start_index:(start_index + 16)]

def invite_friends_2(request, section="not_invited"):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_qs = _invite_friends_2_qs(user, section)
    f_mgr = user.friendship_set    
    return render_to_response(
        "invite_friends_2.html",
        { "friends": f_qs,
          "page": 'friends',
          "section": section,
          "num_registered": f_mgr.filter(registered=True).count(),
          "num_pledged": f_mgr.filter(date_pledged__isnull=False).count(),
          "num_invited": f_mgr.filter(
                Q(invited_with_batch=True) | 
                Q(invited_individually=True)).count(),
          "num_uninvited": f_mgr.filter(
                invited_with_batch=False, 
                invited_individually=False, 
                date_pledged__isnull=True).count(),
          "num_friends": user.num_friends or 0,
          "num_voted": user.num_friends_voted() },
        context_instance=RequestContext(request))

@csrf_exempt
def invite_friends_2_page(request, section):
    start_index = int(request.POST.get("start", 0))
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_qs = _invite_friends_2_qs(user, section, start_index)
    return render_to_response(
        "_invite_friends_page.html",
        { "friends": f_qs },
        context_instance=RequestContext(request))

def missions(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_mgr = user.friendship_set
    context = {
        "page": "missions",
        "num_registered": f_mgr.filter(registered=True).count(),
        "num_pledged": f_mgr.filter(date_pledged__isnull=False).count(),
        "num_friends": user.num_friends or 0,
        "uninvited_batches": user.friendshipbatch_set.filter(
            completely_fetched=True, invite_date__isnull=True),
        "still_loading": not user.friends_fetched,
        "my_city": user.location_city}
    return render_to_response(
        "invite_friends.html",
        context,
        context_instance=RequestContext(request))


@render_json
def submit_pledge(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    explicit_share = request.GET.get('explicit_share', None) == 'true'
    if explicit_share:
        share = requests.post(settings.FACEBOOK_OG_PLEDGE_URL, params={
            'website': settings.BASE_URL + reverse('pledge_object'),
            'access_token': request.facebook['access_token'],
            'fb:explicitly_shared': 'true',
        })
    user.explicit_share = explicit_share
    user.date_pledged = datetime.now()
    user.save()
    update_friends_of.delay(
        user.id, request.facebook["access_token"])
    messages.add_message(
        request, messages.INFO,

        # Translators: message displayed to users in green bar when they pledge to vote
        _("Thank you for pledging to vote!")
    )
    return {"next": reverse("main:invite_friends_2")}


def pledge_explicit_share(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    import pdb
    pdb.set_trace()
    return {"next": reverse("main:invite_friends_2")}


@render_json
def fetch_friends(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if user.friendship_set.filter(registered=True).count() < 4:
        return {"fetched": False}
    friends = user.friendship_set.order_by("-display_ordering")[:4]
    html = render_to_string(
        "_friends.html",
        {"friends": friends},
        context_instance=RequestContext(request))
    return {"fetched": True,
             "html": html}


@render_json
def wont_vote(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.wont_vote_reason = "rather_not_say"
    user.registered = False
    user.save()
    messages.add_message(
        request, messages.INFO,

        # Translators: message displayed to users in green bar when they say they are ineligible to vote
        _("Thank you! Even though you can't vote, you can still invite your friends.")
    )
    return {"next": reverse("main:invite_friends_2")}


@render_json
def im_actually_registered(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.registered = True
    user.save()
    correct_voter(user.fb_uid)
    messages.add_message(
        request, messages.INFO,

        # Translators: message displayed to users in green bar when they are found to already be registered to vote
        _("You're now marked as registered to vote.")
    )
    return {"next": reverse("main:pledge")}


@render_json
def fetch_updated_batches(request):
    _fetch_fb_friends(request)
    batch_ids = request.GET["batchids"]
    if batch_ids == "":
        batch_ids = []
    else:
        batch_ids = set([int(b) for b in batch_ids.split(",")])
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_mgr = user.friendship_set
    batches = user.friendshipbatch_set.filter(
        completely_fetched=True, invite_date__isnull=True)
    htmls = []
    for batch in batches:
        if batch.id not in batch_ids:
            htmls.append(
                render_to_string(
                    "_batch.html", {"batch": batch},
                    context_instance=RequestContext(request)))
    return {
        "num_registered": f_mgr.filter(registered=True).count(),
        "num_pledged": f_mgr.filter(date_pledged__isnull=False).count(),
        "num_friends": user.num_friends or 0,
        "num_processed": f_mgr.all().count(),
        "boxes": htmls,
        "finished": user.friends_fetched}


@render_json
def mark_batch_invited(request):
    batch_id = int(request.GET["batch_id"])
    batch = FriendshipBatch.objects.get(id=batch_id)
    batch.invite_date = datetime.now()
    batch.save()
    batch.friendship_set.all().update(invited_with_batch=True)
    batch.user.save_invited_friends()
    return { "response": "ok" }

@render_json
def mark_individual_invited(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    friendship = user.friendship_set.get(fb_uid=request.GET["fbuid"])
    friendship.invited_individually = True
    friendship.save()

@render_json
def single_user_invited(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.save_invited_friends()
    return { "response": "ok" }

def unregistered_friends_list(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    batches = user.friendshipbatch_set.filter(
        completely_fetched=True, type=BATCH_REGULAR)
    friendships = []
    for batch in batches:
        friendships.extend(list(batch.friendship_set.all()))
    return render_to_response(
        "unregistered_friends_list.html",
        {"friendships": friendships},
        context_instance=RequestContext(request))

def register_widget(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    widget_qs = {
        "first_name": user.first_name,
        "last_name": user.last_name}
    if user.email:
        widget_qs["email"] = user.email
    if user.location_city:
        widget_qs["city"] = user.location_city
        widget_qs["state"] = user.location_state
    if user.birthday:
        widget_qs["dob_month"] = user.birthday.month
        widget_qs["dob_day"] = user.birthday.day
        widget_qs["dob_year"] = user.birthday.year
    return render_to_response(
        "register_widget.html",
        {"widget_qs": urllib.urlencode(widget_qs),
          "page": "register"},
        context_instance=RequestContext(request))

def _mission_friends_qs(user, batch_type, start_index=0):
    return user.friendship_set.filter(
        batch_type=batch_type).order_by("fb_uid")[start_index:(start_index + 12)]

def mission(request, batch_type=BATCH_BARELY_LEGAL):
    batch_type = int(batch_type)
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_qs = FriendshipBatch.objects.filter(user=user, type=batch_type)
    recs = f_qs.filter(invite_date__isnull=True)[:1]
    uninvited_batch = None if len(recs) == 0 else recs[0]
    recs = f_qs.filter(invite_date__isnull=False).order_by("-invite_date")[:1]
    last_invited_batch = None if len(recs) == 0 else recs[0]
    context = {
        "batch_type": batch_type,
        "missions": user.mission_set.all(),
        "uninvited_batch": uninvited_batch,
        "last_invited_batch": last_invited_batch,
        "friends": _mission_friends_qs(user, batch_type) }
    return render_to_response(
        "mission.html",
        context,
        context_instance=RequestContext(request))

@csrf_exempt
def mission_friends_page(request, batch_type):
    start_index = int(request.POST.get("start", 0))
    user = User.objects.get(fb_uid=request.facebook["uid"])
    return render_to_response(
        "_invite_friends_page.html",
        { "friends": _mission_friends_qs(user, batch_type, start_index) },
        context_instance=RequestContext(request))

@csrf_exempt
def mark_mission_batch_invited(request, batch_type):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    batch_type = int(batch_type)
    batch_id = int(request.POST["batch_id"])
    batch = FriendshipBatch.objects.get(id=batch_id)
    if batch.user != user:
        return HttpResponseNotAllowed("not allowed")
    batch.invite_date = datetime.now()
    batch.save()
    batch.friendship_set.all().update(invited_with_batch=True)
    batch.user.save_invited_friends()
    recs = FriendshipBatch.objects.filter(
        user=batch.user, type=batch_type, invite_date__isnull=True)
    uninvited_batch = None if len(recs) == 0 else recs[0]
    return render_to_response(
        "_mission_uninvited_batch.html",
        { "uninvited_batch": uninvited_batch,
          "batch_type": batch_type },
        context_instance=RequestContext(request))

def unsubscribe(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    user.unsubscribed = True
    user.save()
    messages.add_message(
        request, messages.INFO,

        # Translators: message displayed to users in green bar when they unsubscribe from emails
        _("Email notifications are turned off")
    )
    return _index_redirect(user)
