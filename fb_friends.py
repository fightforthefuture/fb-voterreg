import facebook
from voterapi import fetch_voter_from_fb_uid
from main.models import User, Friendship
from django.db import IntegrityError

TARGET_FRIEND_COUNT = 5
NUM_TO_TRY = 50 # limits searching of fb friends in votizen to about 15 seconds

def _find_existing_users(user, friend_uids):
    """ Returns first TARGET_FRIEND_COUNT admirable existing users as Friendships. """
    friendships = []
    for uid in friend_uids:
        results = User.objects.filter(fb_uid=uid)[:1]
        if len(results) == 0:
            continue
        friend = results[0]
        if friend.is_admirable():
            friendships.append(
                Friendship.create(
                    user, friend.fb_uid, friend.name,
                    registered=friend.registered,
                    date_pledged=friend.date_pledged,
                    invited_pledge_count=friend.invited_pledge_count))
            if len(friendships) >= TARGET_FRIEND_COUNT:
                break
    return friendships

def _find_registered_voters(user, access_token, friend_uids, 
                            friend_names, num_needed):
    """ Uses the voting api to return first num_needed registered 
        voters as new Friendships """
    friendships = []
    count = 0
    for uid in friend_uids:
        if count > NUM_TO_TRY:
            break
        count += 1
        print("fetching voter from fb")
        voter = fetch_voter_from_fb_uid(uid, access_token)
        if voter and voter.registered:
            print("found registered voter")
            friendships.append(
                Friendship.create(
                    user, uid, friend_names[uid],
                    registered=True,
                    votizen_id=voter.id))
            if len(friendships) >= num_needed:
                break
    return friendships

def _plain_friendships(user, friend_uids, friend_names):
    friendships = []
    for uid in friend_uids:
        friendships.append(Friendship.create(
                user, uid, friend_names[uid]))
    return friendships

def _make_friendships(user, access_token, fb_friends):
    friend_uids = set(f["id"] for f in fb_friends)
    friend_names = dict((f["id"], f["name"]) for f in fb_friends)
    friendships = _find_existing_users(user, friend_uids)
    if len(friendships) < TARGET_FRIEND_COUNT:
        friendship_uids = set(f.friend_fb_uid for f in friendships)
        friendships.extend(_find_registered_voters(
                user, 
                access_token,
                friend_uids - friendship_uids,
                friend_names,
                TARGET_FRIEND_COUNT - len(friendships)))
    if len(friendships) < TARGET_FRIEND_COUNT:
        friendship_uids = set(f.friend_fb_uid for f in friendships)
        friends_not_added = list(friend_uids - friendship_uids)
        num_needed = TARGET_FRIEND_COUNT - len(friendships)
        friendships.extend(_plain_friendships(
                user, friends_not_added[:num_needed], friend_names))
    for friendship in friendships:
        # possible (but unlikely) that an identical friendship has been 
        # saved by another process.
        try:
            friendship.save()
        except IntegrityError:
            pass

def get_friends(access_token, limit=5000, offset=0):
    graph = facebook.GraphAPI(access_token)
    connections = graph.get_connections(
        "me", "friends", offset=offset, limit=limit)
    return connections["data"]

def fetch_friends(fb_uid, access_token):
    user = User.objects.get(fb_uid=fb_uid)
    if user.friends_fetch_started:
        return
    user.friends_fetch_started = True
    user.save()
    _make_friendships(
        user, access_token, get_friends(access_token, 500))
    user.friends_fetched = True
    user.save()

def update_friends_of(user_id, access_token):
    # modify any existing Friendship records that has this User on 
    # the friend side.
    # add Friendship records for existing Users in our system.
    user = User.objects.get(id=user_id)
    if not user.is_admirable():
        return # no reason to modify/add Friendship records.
    friendships = Friendship.objects.filter(fb_uid=user.fb_uid)
    for friendship in friendships:
        friendship.update_from(user)
        friendship.save()
    fb_friends = get_friends(access_token)
    for fb_friend in fb_friends:
        users = User.objects.filter(fb_uid=fb_friend["id"])[:1]
        if len(users) == 1 and not Friendship.objects.filter(
            user=users[0], fb_uid=user.fb_uid).exists():
            try:
                # TODO give users[0] credit for getting user
                # to join, if applicable.
                friendship = Friendship.create(
                    users[0], user.fb_uid, user.name)
                friendship.update_from(user)
                friendship.save()
            except IntegrityError:
                pass
