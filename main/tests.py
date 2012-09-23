from django.utils import unittest
from django.test.client import Client
from voterapi import Voter
from models import User, Friendship
import fb_friends

def fetch_voter_from_fb_uid(uid, access_token):
    return Voter(uid + "fb", uid in ["1001", "1008", "1009"])

def get_friends(access_token):
    return [{ "name": "friend{0}".format(i),
              "id": "100{0}".format(i) } for i in range(10)]

class FBFriendsTest(unittest.TestCase):
    def test_fetch_friends(self):
        fb_friends.fetch_voter_from_fb_uid = fetch_voter_from_fb_uid
        fb_friends.get_friends = get_friends
        User(fb_uid="100").save()
        fb_friends.fetch_friends("100", "abc")
        user = User.objects.get(fb_uid="100")
        friends = user.friendship_set.order_by("-display_ordering")[:4]
        self.assertEqual(4, len(friends))
        friend_ids = [f.friend_fb_uid for f in friends]
        for id in ["1001", "1008", "1009"]:
            self.assertTrue(id in friend_ids)

# TODO: write test where some friends are already in db.
