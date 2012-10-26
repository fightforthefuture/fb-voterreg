import facebook
from os import environ
import requests
import urllib
from urlparse import urlparse
import sys
from django.db.models import Q, Count
from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response, redirect
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import NoReverseMatch, reverse
from django.http import Http404, HttpResponse, HttpResponseNotAllowed, \
    HttpResponseRedirect
from tasks import fetch_fb_friends, update_friends_of
from decorators import render_json
from voterapi import fetch_voter_from_fb_profile, correct_voter
from models import User, FriendshipBatch, BATCH_REGULAR, VotingBlock, VotingBlockMember
from datetime import datetime, date, time
from fb_utils import FacebookProfile, opengraph_url
from django.core.mail import EmailMultiAlternatives
from models import BATCH_NEARBY, Friendship, BADGE_CUTOFFS
import logging
import forms

class OGObjectView(TemplateView):
    """
    The view used to serve the OpenGraph objects published whenever a user
    pledges to vote.
    """

    def get_context_data(self, **kwargs):
        context = super(OGObjectView, self).get_context_data(**kwargs)
        context['base_url'] = settings.BASE_URL
        context['canvas_url'] = settings.FACEBOOK_CANVAS_PAGE
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID

        environment = environ.get("RACK_ENV", 'dev')
        namespace_map = {
            'dev': '-dev',
            'staging': '-stag',
            'production': '',
        }
        context['og_namespace'] = namespace_map[environment]

        return context


class VotingBlockShareView(DetailView):
    """

    """
    model = VotingBlock
    template_name = 'voting_blocks_share.html'
    context_object_name = 'block'

    def get_context_data(self, **kwargs):
        context = super(VotingBlockShareView, self).get_context_data(**kwargs)
        context['facebook_app_id'] = settings.FACEBOOK_APP_ID
        context['canvas_url'] = settings.FACEBOOK_CANVAS_PAGE
        return context


class NotificationCheckView(TemplateView):
    template_name = 'notifications.html'


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
        update_friends_of.delay(user.id)
        messages.add_message(
            request, messages.INFO,
            # Translators: message displayed to users when they unpledge
            _("Sorry to hear that you're no longer pledging to vote.")
        )
        return redirect('main:my_vote')
    return HttpResponseNotAllowed()


@csrf_exempt
def index(request):
    request.session['after'] = request.GET.get("after", None)
    if request.method == "POST":
        response = _post_index(request)
        if response:
            return response
    user = User.objects.get(fb_uid=request.facebook["uid"])
    query_string = request.META["QUERY_STRING"]
    if user.data_fetched:
        target_url = request.GET.get("target", None)
        if target_url:
            try:
                return redirect(target_url)
            except NoReverseMatch:
                raise Http404
        else:
            return _index_redirect(user, query_string)
    return render_to_response(
        "loading.html",
        context_instance=RequestContext(request))


def my_vote(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    after = request.session.get('after', None)

    if user.pledged and user.voted and not 'nav' in request.GET:
        if after:
            return redirect(after)
        return redirect('main:invite_friends_2')

    if user.pledged:

        # The user has explicitly navigated here, either from the navigation or
        # the pledge form, so we will show them the voting form. In other
        # cases, we want to send them to the invite friends page to avoid
        # repeatedly annoying them.
        if 'force' in request.GET:
            return redirect('main:my_vote_vote')

        if after:
            return redirect(after)

        return redirect('main:invite_friends_2')

    else:
        return redirect('main:my_vote_pledge')


def my_vote_pledge(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if request.GET.get("from_widget", False):
        user.registered = True
        user.used_registration_widget = True
        user.save()
        update_friends_of.delay(user.id)
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
    after = request.session.get('after', None)

    if request.method == 'GET':
        return render_to_response("my_vote_vote.html", {
            'page': 'my_vote',
            'section': 'vote',
            'user': user,
        }, context_instance=RequestContext(request))

    elif request.method == 'POST':
        explicit_share = request.POST.get('tell-friends', '') == 'on'
        if explicit_share:
            og_url = opengraph_url(request, settings.FACEBOOK_OG_VOTE_ACTION)
            share = requests.post(og_url, params={
                'election_obj': settings.BASE_URL + reverse('vote_object'),
                'access_token': request.facebook['access_token'],
                'fb:explicitly_shared': 'true',
            })
            print 'Explicit share vote response: %s' % share.status_code
            print share.content

        user.explicit_share_vote = explicit_share

        if 'yes' in request.POST:
            user.date_voted = datetime.now()
            try:
                friendships = Friendship.objects.filter(fb_uid=user.fb_uid)
                for friendship in friendships:
                    friendship.date_voted = datetime.now()
                    friendship.save()
            except Friendship.DoesNotExist:
                pass
            messages.add_message(
                request, messages.INFO,
                # Translators: message displayed to users in when they mark themselves as having voted.
                _("Your voice was heard! Make sure your friends' voices are also heard:")
            )
            if after:
                redirect_view = after
            else:
                redirect_view = 'main:invite_friends_2'
        else:
            user.date_voted = None
            messages.add_message(
                request, messages.INFO,
                # Translators: message displayed to users in when they mark themselves as not having voted.
                _("Got it, you haven't voted yet. Don't forget!")
            )
            if after:
                redirect_view = after
            else:
                redirect_view = 'main:invite_friends_2'
        user.save()

        update_friends_of.delay(user.id)

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
            update_friends_of.delay(user.id)
        _fetch_fb_friends(request)
    redirect_url = reverse("main:pledge")
    return HttpResponse(redirect_url, content_type="text/plain")

def _send_join_email(user, request):
    today = date.today()
    num_days = (date(2012, 11, 6) - today).days
    invite_friends_url = reverse('main:invite_friends_2')
    unsubscribe_url = reverse('main:unsubscribe')
    context = {
        "first_name": user.first_name,
        "num_days": num_days,
        "invite_friends_url": invite_friends_url,
        "unsubscribe_url": unsubscribe_url }
    html_body = render_to_string(
        "join_email.html",
        context,
        context_instance=RequestContext(request))
    text_body = render_to_string(
        "join_email.txt",
        context,
        context_instance=RequestContext(request))
    if user.email:
        msg = EmailMultiAlternatives(
            # Translators: subject of email sent to users when they join the app
            _("Get your friends to pledge."),
            text_body,
            settings.EMAIL_SENDER,
            [user.email],
            headers={ 'Reply-To': 'info@votewithfriends.net',
                      "From": "Vote with Friends <{0}>".format(settings.EMAIL_SENDER)})
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)

def _friend_list(user):
    friends = list(user.friendship_set.order_by("-display_ordering")[:4])
    return sorted(friends, key=lambda f: f.name)


def pledge(request):
    return redirect('main:my_vote_pledge')


def _invite_friends_2_qs(user, section, start_index=0):
    if section == "not_invited":
        f_qs = user.friends.personally_invited(status=False).order_by('?')
    elif section in ["not_pledged", "invited"]:
        f_qs = user.friends.invited_not_pledged()
    elif section == "registered":
        f_qs = user.friends.registered()
    elif section == "pledged":
        f_qs = user.friends.pledged()
    elif section == "voted":
        f_qs = user.friends.voted()
    return f_qs[start_index:(start_index + 16)]


def invite_friends_2(request, section="not_invited"):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_qs = _invite_friends_2_qs(user, section)
    return render_to_response("invite_friends_2.html", {
        "friends": f_qs,
        "page": 'friends',
        "section": section,
        "num_registered": user.friends.registered().count(),
        "num_pledged": user.friends.pledged().count(),
        "num_not_pledged": user.friends.invited_not_pledged().count(),
        "num_uninvited": user.friends.personally_invited(status=False).count(),
        "num_friends": user.num_friends or 0,
        "num_voted": user.friends.voted().count()
    }, context_instance=RequestContext(request))

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
    context = {
        "page": "missions",
        "num_registered": user.friends.registered().count(),
        "num_pledged": user.friends.pledged().count(),
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
        og_url = opengraph_url(request, settings.FACEBOOK_OG_PLEDGE_ACTION)
        share = requests.post(og_url, params={
            'vote_obj': settings.BASE_URL + reverse('pledge_object'),
            'access_token': request.facebook['access_token'],
            'fb:explicitly_shared': 'true',
        })
        print 'Explicit share pledge response: %s' % share.status_code
        print share.content
    user.explicit_share = explicit_share
    user.date_pledged = datetime.now()
    user.save()
    update_friends_of.delay(user.id)
    messages.add_message(
        request, messages.INFO,

        # Translators: message displayed to users in green bar when they pledge to vote
        _("Thank you for pledging to vote!")
    )
    return {"next": reverse("main:my_vote") + '?force'}


@render_json
def fetch_friends(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    if user.friends().registered().count() < 4:
        return {"fetched": False}
    html = render_to_string(
        "_friends.html",
        {"friends": _friend_list(user) },
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
        "num_registered": user.friends.registered().count(),
        "num_pledged": user.friends.pledged().count(),
        "num_friends": user.num_friends or 0,
        "num_processed": user.friends.all().count(),
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

def friends_list(request):
    graph = facebook.GraphAPI(request.facebook["access_token"])
    q = ("SELECT uid, name, first_name, last_name, "
         "birthday_date, hometown_location, current_location "
         "FROM user "
         "WHERE uid in (SELECT uid2 FROM friend WHERE uid1 = me())")
    results = graph.fql(q)
    return render_to_response(
        "friends_list.html",
        { "friendships": results },
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

def mission(request, batch_type=BATCH_NEARBY):
    batch_type = int(batch_type)
    user = User.objects.get(fb_uid=request.facebook["uid"])
    f_qs = FriendshipBatch.objects.filter(user=user, type=batch_type)
    recs = f_qs.filter(invite_date__isnull=True)[:2]
    uninvited_batch = None if len(recs) < 1 else recs[0]
    num_invited = user.friends.filter(batch_type=batch_type).invited().count()
    num_pledged = user.friends.filter(batch_type=batch_type).pledged().count()
    num_friends = user.friends.filter(batch_type=batch_type).count()
    badge_cutoffs = filter(lambda x: x<=num_friends, BADGE_CUTOFFS)
    context = {
        "page": "missions",
        "batch_type": batch_type,
        "missions": user.mission_set.all(),
        "uninvited_batch": uninvited_batch,
        "friends": _mission_friends_qs(user, batch_type), 
        "num_invited": num_invited,
        "num_pledged": num_pledged,
        "num_friends": num_friends,
        "badge_cutoffs": badge_cutoffs }
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

@render_json
def mark_mission_batch_invited(request, batch_type):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    batch_type = int(batch_type)
    batch_id = int(request.GET["batch_id"])
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
    html = render_to_string(
        "_mission_uninvited_batch.html",
        { "uninvited_batch": uninvited_batch,
          "batch_type": batch_type },
        context_instance=RequestContext(request))
    num_invited = user.friends.filter(batch_type=batch_type).invited().count()
    return { "html": html, 
             "num_invited": num_invited,
             "num_friends": user.friendship_set.filter(batch_type=batch_type).count() }

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

def _voting_blocks_search(user, myvbs, filter=None, text=None, skip=0, take=10):
    filter = filter if filter in ['popular', 'near', 'friends'] else 'popular'
    result = {'filters': [], 'list': [] }

    myvbids = [myvb.id for myvb in myvbs]
    baseq = VotingBlock.objects.all()
    #baseq = VotingBlock.objects.filter(~Q(id__in=myvbids))

    #popular
    popularq = baseq\
        .annotate(count=Count('votingblockmember'))
    if text:
        popularq = popularq.filter(Q(name__icontains=text) | Q(description__icontains=text))
    result['filters'].append({'name': 'popular', 'title': 'Most popular', 'active': filter == 'popular'})
    query = popularq.order_by('-count')

    #near
    nearq = baseq\
        .filter(Q(created_by__location_city=user.location_city, created_by__location_state=user.location_state)\
                | Q(created_by__location_state=user.location_state))\
        .extra(select={'distance': "CASE WHEN location_city='%s' AND location_state='%s' THEN 2 WHEN location_state='%s' THEN 1 ELSE 0 END"\
                % (user.location_city, user.location_state, user.location_state,)})\
        .order_by('-distance')
    if text:
        nearq = nearq.filter(Q(name__icontains=text) | Q(description__icontains=text))
    result['filters'].append({'name': 'near', 'count': nearq.count(), 'title': 'Near me', 'active': filter == 'near'})
    if filter == 'near':
        query = nearq

    #friends
    friendsq = baseq\
        .filter(votingblockmember__member__friendship__fb_uid=user.fb_uid)\
        .distinct()\
        .annotate(count=Count('votingblockmember'))
    if text:
        friendsq = friendsq.filter(Q(name__icontains=text) | Q(description__icontains=text))
    result['filters'].append({'name': 'friends', 'count': friendsq.count(), 'title': 'Friends are members', 'active': filter == 'friends'})
    if filter == 'friends':
        query = friendsq.order_by('-count')

    #apply
    #TODO: full text search

    result['list'] = []
    for item in query[skip:skip+take]:
        item.joined = item.id in myvbids
        result['list'].append(item)

    return result


def voting_blocks(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    myvbs = VotingBlock.objects.filter(votingblockmember__member=user).order_by('-votingblockmember__joined')
    context = {
        "page": "voting_blocks",
        "voting_block_note": request.COOKIES.get('voting_block_note', None),
        "my_voting_blocks": myvbs,
        "voting_blocks": _voting_blocks_search(user, myvbs, 'popular')
    }
    return render_to_response(
        "voting_blocks.html",
        context,
        context_instance=RequestContext(request))

def voting_blocks_search(request):
    user = User.objects.get(fb_uid=request.facebook["uid"])
    myvbs = VotingBlock.objects.filter(votingblockmember__member=user)
    skip = int(request.GET.get('skip', 0))
    filter = request.GET.get('filter', None)
    text = request.GET.get('text', None)
    if skip > 0:
        template = "_voting_blocks_results_list.html"
    else:
        template = "_voting_blocks_results.html"
    return render_to_response(
        template,
        { 'voting_blocks': _voting_blocks_search(user, myvbs, filter, text, skip) },
        context_instance=RequestContext(request))


def voting_blocks_create(request):
    if request.POST:
        form = forms.VotingBlockForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.get(fb_uid=request.facebook["uid"])
            form.instance.created_by = user
            form.save()
            VotingBlockMember.objects.create(member=user, voting_block=form.instance, joined=datetime.now())
            return HttpResponseRedirect(reverse('main:voting_blocks_item', kwargs={'id': form.instance.id}))
    else:
        form = forms.VotingBlockForm()
    context = {
        "form": form,
        "page": "voting_blocks",
    }
    return render_to_response(
        "voting_blocks_create.html",
        context,
        context_instance=RequestContext(request))

def _members_qs(user, section, voting_block):
    if section == 'members':
        return User.objects.filter(votingblockmember__voting_block=voting_block)
    elif section == 'voted':
        return User.objects.filter(votingblockmember__voting_block=voting_block, date_voted__isnull=False)
    elif section == 'not_voted':
        return User.objects.filter(votingblockmember__voting_block=voting_block, date_voted__isnull=True)
    elif section == 'friends':
        return User.objects.filter(votingblockmember__voting_block=voting_block, friendship__fb_uid=user.fb_uid)
    elif section == 'not_invited':
        #return user.friends.filter(~Q(fb_uid__in=\
        #    User.objects.filter(votingblockmember__voting_block=voting_block).values_list('fb_uid', flat=True)))
        return user.friends.filter(batch_type=BATCH_REGULAR)

def voting_blocks_item(request, id, section=None):
    id = int(id)
    voting_block = VotingBlock.objects.get(id=id)
    user = User.objects.get(fb_uid=request.facebook["uid"])
    section = section or 'not_invited'
    sections = [
        {'name': 'members', 'count': _members_qs(user, 'members', voting_block).count(), 'title': 'Members'},
        {'name': 'voted', 'count': _members_qs(user, 'voted', voting_block).count(), 'title': 'Voted'},
        {'name': 'not_voted', 'count': _members_qs(user, 'not_voted', voting_block).count(), 'title': 'Haven\'t Voted'},
        {'name': 'friends', 'count': _members_qs(user, 'friends', voting_block).count(), 'title': 'My Friends'},
        {'name': 'not_invited', 'count': _members_qs(user, 'not_invited', voting_block).count(), 'title': 'Invite Friends'},
    ]
    context = {
        "page": "voting_blocks",
        "sections": sections,
        "section": section,
        "voting_block": voting_block,
        "voting_block_members_count": VotingBlockMember.objects.filter(voting_block_id=id).count(),
        "voting_block_members_today_count": VotingBlockMember.objects.filter(voting_block_id=id,
            joined__gt=datetime.combine(datetime.now(), time.min)).count(),
        "voting_block_joined": VotingBlockMember.objects.filter(member=user, voting_block=id).count() > 0
    }

    if section == "not_invited":
        batch_type = int(BATCH_REGULAR)
        user = User.objects.get(fb_uid=request.facebook["uid"])
        f_qs = FriendshipBatch.objects.filter(user=user, type=batch_type)
        recs = f_qs.filter(invite_date__isnull=True)[:2]
        uninvited_batch = None if len(recs) < 1 else recs[0]
        num_invited = user.friends.filter(batch_type=batch_type).invited().count()
        num_pledged = user.friends.filter(batch_type=batch_type).pledged().count()
        num_friends = user.friends.filter(batch_type=batch_type).count()
        badge_cutoffs = filter(lambda x: x<=num_friends, BADGE_CUTOFFS)
        context.update({
            "batch_type": batch_type,
            "uninvited_batch": uninvited_batch,
            "friends": _mission_friends_qs(user, batch_type),
            "num_invited": num_invited,
            "num_pledged": num_pledged,
            "num_friends": num_friends,
            "badge_cutoffs": badge_cutoffs
        })
    else:
        context.update({
            "dont_friendship": True,
            "dont_status": True,
            "friends": _members_qs(user, section, voting_block)[:16],
        })

    return render_to_response(
        "voting_blocks_item.html",
        context,
        context_instance=RequestContext(request))

@csrf_exempt
def voting_blocks_item_page(request, id, section):
    id = int(id)
    voting_block = VotingBlock.objects.get(id=id)
    user = User.objects.get(fb_uid=request.facebook["uid"])
    start = int(request.POST.get('start', 0))
    context = { "voting_block": voting_block }
    if section == "not_invited":
        context.update({
            'friends': _mission_friends_qs(user, BATCH_REGULAR, start)
        })
    else:
        context.update({
            'friends': _members_qs(user, section, voting_block)[start:start+16],
            "dont_friendship": True,
            "dont_status": True,
        })
    return render_to_response(
        "_invite_friends_page.html",
        context,
        context_instance=RequestContext(request))


def voting_blocks_item_join(request, id):
    id = int(id)
    try:
        VotingBlockMember.objects.create(
            member=User.objects.get(fb_uid=request.facebook["uid"]), voting_block_id=id, joined=datetime.now())
    except:
        pass
    return HttpResponseRedirect(reverse('main:voting_blocks_item', kwargs={'id': id}))

def voting_blocks_item_leave(request, id):
    id = int(id)
    VotingBlockMember.objects.filter(
        member=User.objects.get(fb_uid=request.facebook["uid"]), voting_block=id).delete()
    return HttpResponseRedirect(reverse('main:voting_blocks_item', kwargs={'id': id}))

def test_logger_error(request):
    logging.error("hit test logger error page")
    return render_to_response("500.html")
