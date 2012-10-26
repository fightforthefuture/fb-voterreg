import facebook
from voterapi import fetch_voters_from_fb_profiles
from main.models import User, Friendship, BATCH_NEARBY, \
    BATCH_FAR_FROM_HOME, BATCH_BARELY_LEGAL, WonBadge, \
    LastAppNotification, BADGE_PLEDGED, BADGE_VOTED
from django.db import IntegrityError
from fb_utils import FacebookProfile
from datetime import datetime, date
import logging

def _create_from_existing_users(user, fb_friends):
    """ Creates Friendships using existing Users """
    found_uids = set()
    for fb_friend in fb_friends:
        uid = fb_friend["uid"]
        results = User.objects.filter(fb_uid=uid)[:1]
        if len(results) > 0:
            found_uids.add(uid)
            try:
                Friendship.create_from(user, results[0]).save()
            except IntegrityError:
                pass
    return found_uids

def _initial_batch_type(user, profile):
    if profile.location and profile.location == user.location_name:
        return BATCH_NEARBY
    elif profile.far_from_home():
        return BATCH_FAR_FROM_HOME
    elif profile.dob and date.today().year - profile.dob.year < 22:
        return BATCH_BARELY_LEGAL
    return None

def _make_initial_batches(user, fb_friends, found_uids):
    newly_found_uids = set()
    for fb_friend in fb_friends:
        uid = fb_friend["uid"]
        if uid in found_uids:
            continue
        profile = FacebookProfile(fb_friend)
        batch_type = _initial_batch_type(user, profile)
        if not batch_type:
            continue
        newly_found_uids.add(uid)
        f = Friendship.create_from_fb_profile(user, profile)
        try:
            f.save()
        except IntegrityError:
            pass
    user.friendshipbatch_set.filter(type=BATCH_NEARBY).update(completely_fetched=True)
    user.friendshipbatch_set.filter(type=BATCH_FAR_FROM_HOME).update(completely_fetched=True)
    user.friendshipbatch_set.filter(type=BATCH_BARELY_LEGAL).update(completely_fetched=True)
    return newly_found_uids

def _make_main_batches(user_id, access_token, fb_friends, found_uids):
    voters = fetch_voters_from_fb_profiles(
        [FacebookProfile(f) for f in fb_friends if f["uid"] not in found_uids])
    voter_map = dict((v.fb_uid, v) for v in voters)
    user = User.objects.get(id=user_id)
    user.update_friends_fetch()
    user.save()
    for fb_friend in fb_friends:
        uid = fb_friend["uid"]
        if uid in found_uids:
            continue
        if Friendship.objects.filter(user=user, fb_uid=uid).count() > 0:
            continue
        if uid not in voter_map:
            logging.error("found uid not in voter map: {0}".format(uid))
            continue
        profile = FacebookProfile(fb_friend)
        voter = voter_map[uid]
        f = Friendship.create_from_fb_profile(user, profile)
        if voter and voter.registered:
            f.registered = True
            f.votizen_id = voter.id
        try:
            f.save()
        except IntegrityError:
            pass

def _update_registered_status_of_all(user_id, fb_friends):
    user = User.objects.get(id=user_id)
    profiles_to_update = []
    for fb_friend in fb_friends:
        f = Friendship.objects.filter(user=user, fb_uid=fb_friend["uid"]).all()[:1]
        if len(f) == 0:
            continue
        f = f[0]
        if not f.votizen_id:
            profiles_to_update.append(FacebookProfile(fb_friend))
    voters = fetch_voters_from_fb_profiles(profiles_to_update)
    for voter in voters:
        f = Friendship.objects.get(user=user, fb_uid=voter.fb_uid)
        f.votizen_id = voter.id
        f.registered = voter.registered
        f.save()

def _make_friendships(user_id, access_token, fb_friends):
    user = User.objects.get(id=user_id)
    found_uids = _create_from_existing_users(user, fb_friends)
    _update_friends_fetch(user_id)
    found_uids = found_uids.union(
        _make_initial_batches(user, fb_friends, found_uids))
    _update_friends_fetch(user_id)
    _make_main_batches(user_id, access_token, fb_friends, found_uids)

def _update_friends_fetch(user_id):
    user = User.objects.get(id=user_id)
    user.update_friends_fetch()
    user.save()

def _definitely_foreign(fb_record):
    hometown = fb_record.get("hometown_location", None)
    location = fb_record.get("current_location", None)
    if not hometown or not location:
        return False
    return hometown["country"] != "United States" and \
        location["country"] != "United States"

def get_friends(access_token, limit=5000, offset=0):
    graph = facebook.GraphAPI(access_token)
    q = ("SELECT uid, name, first_name, last_name, "
             "birthday_date, hometown_location, current_location "
         "FROM user "
         "WHERE uid in (SELECT uid2 FROM friend WHERE uid1 = me())")
    results = graph.fql(q)
    return [result for result in results if not _definitely_foreign(result)]

def fetch_friends(fb_uid, access_token):
    friends = get_friends(access_token)
    user = User.objects.get(fb_uid=fb_uid)
    user.update_friends_fetch()
    user.num_friends = len(friends)
    user.save()

    _make_friendships(user.id, access_token, friends)

    user = User.objects.get(fb_uid=fb_uid)
    user.friends_fetched = True
    user.save()

    user.friendshipbatch_set.all().update(completely_fetched=True)

    _update_registered_status_of_all(user.id, friends)

def _award_badges(friendship):
    user = friendship.user
    pledge_awarded = WonBadge.award_badge(user, BADGE_PLEDGED)
    voted_awarded = WonBadge.award_badge(user, BADGE_VOTED)
    LastAppNotification.notify_user(user)

def update_friends_of(user_id):
    # modify any existing Friendship records that has this User on 
    # the friend side.
    user = User.objects.get(id=user_id)
    if not user.is_admirable():
        return # no reason to modify Friendship records.
    friendships = Friendship.objects.filter(fb_uid=user.fb_uid)
    for friendship in friendships:
        friendship.update_from(user)
        friendship.save()
        _award_badges(friendship)
