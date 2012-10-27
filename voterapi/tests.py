from django.utils import unittest
from django.test.client import Client
from fb_utils import FacebookProfile
from voterapi.models import VoterRecord
import voterapi
import json

RESPONSE_HIT = 1
RESPONSE_MISS = 2
RESPONSE_ERROR = 3

def _fake_profiles(num):
    profiles = []
    for i in range(num):
        fql = { "uid": "uid{0}".format(i),
                "name": "a b",
                "first_name": "a",
                "last_name": "b",
                "current_location": { "name": "a", "city": "b", "state": "Massachusetts" } }
        profiles.append(FacebookProfile(fql))
    return profiles

def _votizen_response(*responses):
    response = []
    for r in responses:
        if r == RESPONSE_HIT:
            response.append(
                {u'body': u'{"meta": {"limit": 20, "next": null, "offset": 0, "previous": null, "total_count": 1}, "objects": [{"id": "232175344", "is_registered_voter": true, "resource_uri": "/v1/voter/232175344/", "voter_data_uris": {"voter_districts_uri": "/v1/voter/232175344/districts/", "voter_record_uri": "/v1/voter/232175344/record/"}}]}', 
                 u'headers': {u'x-ratelimit-remaining': u'598', u'x-ratelimit-limit': u'600', u'x-ratelimit-reset': u'1351254364'}, 
                 u'status_code': 200})
        elif r == RESPONSE_MISS:
            response.append(
                {u'body': u'{"meta": {"limit": 20, "next": null, "offset": 0, "previous": null, "total_count": 0}, "objects": []}', 
                 u'headers': {u'x-ratelimit-remaining': u'599', u'x-ratelimit-limit': u'600', u'x-ratelimit-reset': u'1351254364'}, 
                 u'status_code': 200})
        else:
            response.append({ "status_code": 403 })
    return response

def _includes_addresses(requests):
    for request in requests:
        uri = request["relative_uri"]
        if "city=b" not in uri:
            return False
    return True

class FBFriendsTest(unittest.TestCase):
    def setUp(self):
        VoterRecord.objects.all().delete()

    def _assert_uids_present(self, voters):
        for i in range(3):
            uid = "uid{0}".format(i)
            self.assertTrue(len([v for v in voters if v.fb_uid == uid]) == 1)

    def test_fetch_friends_initial_miss(self):
        counter = [0]
        requests = []
        def batch_post(request):
            requests.append(request)
            counter[0] += 1
            if counter[0] == 1:
                return 200, _votizen_response(RESPONSE_HIT, RESPONSE_MISS, RESPONSE_MISS)
            else:
                requests.append(request)
                return 200, _votizen_response(RESPONSE_HIT, RESPONSE_MISS)
        voterapi._batch_post = batch_post
        voters = voterapi.fetch_voters_from_fb_profiles(_fake_profiles(3))
        self.assertEquals(3, len(requests[0]))
        self.assertFalse(_includes_addresses(requests[0]))
        self.assertEquals(2, len(requests[1]))
        self.assertTrue(_includes_addresses(requests[1]))
        self.assertEquals(3, len(voters))
        self.assertEquals(2, len([v for v in voters if v.registered]))
        self._assert_uids_present(voters)

    def test_fail_on_first_request(self):
        counter = [0]
        requests = []
        def batch_post(request):
            requests.append(request)
            counter[0] += 1
            if counter[0] == 1:
                return 200, _votizen_response(RESPONSE_HIT, RESPONSE_MISS, RESPONSE_ERROR)
            elif counter[0] == 2:
                return 200, _votizen_response(RESPONSE_MISS)
            else:
                return 200, _votizen_response(RESPONSE_HIT)
        voterapi._batch_post = batch_post
        voters = voterapi.fetch_voters_from_fb_profiles(_fake_profiles(3))
        self.assertEquals(3, len(requests))
        self.assertEquals(3, len(voters))
        self.assertFalse(_includes_addresses(requests[2]))
        self.assertEquals(2, len([v for v in voters if v.registered]))
        self._assert_uids_present(voters)
        
    def test_fail_on_second_request(self):
        counter = [0]
        requests = []
        def batch_post(request):
            requests.append(request)
            counter[0] += 1
            if counter[0] == 1:
                return 200, _votizen_response(RESPONSE_HIT, RESPONSE_MISS, RESPONSE_MISS)
            elif counter[0] == 2:
                return 200, _votizen_response(RESPONSE_MISS, RESPONSE_ERROR)
            else:
                return 200, _votizen_response(RESPONSE_HIT)
        voterapi._batch_post = batch_post
        voters = voterapi.fetch_voters_from_fb_profiles(_fake_profiles(3))
        self.assertEquals(3, len(requests))
        self.assertEquals(3, len(voters))
        self.assertTrue(_includes_addresses(requests[2]))
        self.assertEquals(2, len([v for v in voters if v.registered]))
        self._assert_uids_present(voters)

    def test_preexisting_voter_record(self):
        v = VoterRecord(
            fb_uid="uid0",
            votizen_id="a",
            registered=True)
        v.save()
        counter = [0]
        requests = []
        def batch_post(request):
            requests.append(request)
            counter[0] += 1
            return 200, _votizen_response(RESPONSE_MISS, RESPONSE_MISS)
        voterapi._batch_post = batch_post
        voters = voterapi.fetch_voters_from_fb_profiles(_fake_profiles(3))
        self.assertEquals(2, len(requests))
        self.assertEquals(3, len(voters))
        self.assertEquals(1, len([v for v in voters if v.registered]))
        self._assert_uids_present(voters)

