import requests
from django.conf import settings
from models import VoterRecord, APIHitCount
import facebook
from fb_utils import FacebookProfile
from django.db import IntegrityError
from random import choice
import string

MAX_API_HITS = 100000
_URL = "https://api.votizen.com/v1/voter/"
_FETCH_VOTER_PARAMS = \
    set(["first_name", "middle_name", "last_name", "street",
         "city", "state", "zip", "dob_year", "dob_month", "dob_day"])

class Voter(object):
    def __init__(self, id, registered):
        self.id = id
        self.registered = registered

def _requests_exhausted():
    return False

def _params_from_fb_profile(fb_profile, include_address):
    profile = FacebookProfile(fb_profile)
    params = {
        "first_name": profile.first_name,
        "last_name": profile.last_name }
    if include_address and profile.location_city:
        params["city"] = profile.location_city
        params["state"] = profile.location_state
    if profile.dob_month:
        params["dob_month"] = profile.dob_month
        params["dob_day"] = profile.dob_day
    if profile.dob_year:
        params["dob_year"] = profile.dob_year
    return params

def fetch_voter_from_fb_profile(fb_profile):
    fb_uid = fb_profile["id"]
    existing_records = VoterRecord.objects.filter(fb_uid=fb_uid)[:1]
    if len(existing_records) > 0:
        existing_record = existing_records[0]
        return Voter(existing_record.votizen_id,
                     existing_record.registered)
    params = _params_from_fb_profile(fb_profile, False)
    voter = fetch_voter(**params)
    if not voter:
        params = _params_from_fb_profile(fb_profile, True)
        voter = fetch_voter(**params)
    if voter:
        try:
            VoterRecord(fb_uid=fb_uid,
                        votizen_id=voter.id,
                        registered=voter.registered).save()
        except IntegrityError:
            pass
    return voter

def fetch_voter(**kwargs):
    if settings.USE_FAKE_VOTIZEN_API:
        if choice([True, True, False]):
            return Voter("".join([choice(string.letters) for i in range(10)]),
                         choice([True, False]))
        else:
            return None
    if not all(k in _FETCH_VOTER_PARAMS for k, v in kwargs.items()):
        raise AttributeError("Invalid arguments")
    hit_count = APIHitCount.next()
    if hit_count > MAX_API_HITS:
        return None
    params = kwargs.copy()
    params["api_key"] = settings.VOTIZEN_API_KEY
    response = requests.get(_URL, params=params).json
    if response and "objects" in response and len(response["objects"]) > 0:
        obj = response["objects"][0]
        return Voter(obj["id"], obj["is_registered_voter"])
    else:
        return None

def correct_voter(fb_uid):
    voter_records = VoterRecord.objects.filter(fb_uid=fb_uid)[:1]
    if len(voter_records) > 0:
        v = voter_records[0]
        v.registered = True
        v.save()
