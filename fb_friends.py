import facebook
from voterapi import fetch_voter_from_fb_profile
from main.models import User, Friendship, BATCH_SIZE, BATCH_RANDOM
from django.db import IntegrityError
from fb_utils import FacebookProfile

def _create_from_existing_users(user, fb_friends):
    """ Creates Friendships using existing Users """
    found_uids = set()
    for fb_friend in fb_friends:
        uid = fb_friend["id"]
        results = User.objects.filter(fb_uid=uid)[:1]
        if len(results) > 0:
            found_uids.add(uid)
            try:
                Friendship.create_from(user, results[0]).save()
            except IntegrityError:
                pass
    return found_uids

def _make_random_batches(user, fb_friends, found_uids):
    newly_found_uids = set()
    END_COUNT = BATCH_SIZE * 3
    count = 0
    for fb_friend in fb_friends:
        uid = fb_friend["id"]
        if uid in found_uids:
            continue
        newly_found_uids.add(uid)
        f = Friendship.create(user, uid, fb_friend["name"])
        f.is_random = True
        try:
            f.save()
            count += 1
        except IntegrityError:
            pass
        if count >= END_COUNT:
            break
    user.friendshipbatch_set.filter(type=BATCH_RANDOM).update(completely_fetched=True)
    return newly_found_uids

def _make_main_batches(user_id, access_token, fb_friends, found_uids):
    graph = facebook.GraphAPI(access_token)
    for fb_friend in fb_friends:
        user = User.objects.get(id=user_id)
        uid = fb_friend["id"]
        if uid in found_uids:
            continue
        if Friendship.objects.filter(user=user, fb_uid=uid).count() > 0:
            continue
        user.update_friends_fetch()
        user.save()
        fb_profile = graph.get_object(uid)
        profile = FacebookProfile(fb_profile)
        voter = fetch_voter_from_fb_profile(fb_profile)
        f = Friendship.create(user, uid, fb_friend["name"])
        f.birthday = profile.dob
        f.location_name = profile.location or ""
        f.far_from_home = profile.far_from_home()
        if voter and voter.registered:
            f.registered = True
            f.votizen_id = voter.id
            print("registered")
        else:
            print("unregistered")
        try:
            f.save()
        except IntegrityError:
            pass

def _make_friendships(user_id, access_token, fb_friends):
    user = User.objects.get(id=user_id)
    found_uids = _create_from_existing_users(user, fb_friends)
    _update_friends_fetch(user_id)
    found_uids = found_uids.union(
        _make_random_batches(user, fb_friends, found_uids))
    _update_friends_fetch(user_id)
    _make_main_batches(user_id, access_token, fb_friends, found_uids)

def _update_friends_fetch(user_id):
    user = User.objects.get(id=user_id)
    user.update_friends_fetch()
    user.save()

def get_friends(access_token, limit=5000, offset=0):
    graph = facebook.GraphAPI(access_token)
    connections = graph.get_connections(
        "me", "friends", offset=offset, limit=limit)
    return connections["data"]

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

def update_friends_of(user_id, access_token):
    # modify any existing Friendship records that has this User on 
    # the friend side.
    # add Friendship records for existing Users in our system.
    user = User.objects.get(id=user_id)
    if not user.is_admirable():
        return # no reason to modify Friendship records.
    friendships = Friendship.objects.filter(fb_uid=user.fb_uid)
    for friendship in friendships:
        # TODO: maybe give inviter credit
        friendship.update_from(user)
        friendship.save()
