from django.conf import settings
from models import VoterRecord
from fb_utils import FacebookProfile
from django.db import IntegrityError
from random import choice, random
from urllib import urlencode
import requests
import json
import facebook
import time
import string
import logging

logger = logging.getLogger(__name__)

_URL = "https://api.votizen.com/v1/voter/"
_RELATIVE_URL = "/v1/voter/"
_BATCH_URL = "https://api.votizen.com/v1/batch/"
_FETCH_VOTER_PARAMS = \
    set(["first_name", "middle_name", "last_name", "street",
         "city", "state", "zip", "dob_year", "dob_month", "dob_day"])

class Voter(object):
    def __init__(self, id, registered):
        self.id = id
        self.registered = registered

def _requests_exhausted():
    return False

def _params_from_fb_profile(profile, include_address):
    params = {
        "first_name": profile.first_name,
        "last_name": profile.last_name }
    if include_address and profile.location_city and profile.location_state:
        params["city"] = profile.location_city
        params["state"] = profile.location_state
    if profile.dob_month:
        params["dob_month"] = str(profile.dob_month)
        params["dob_day"] = str(profile.dob_day)
    if profile.dob_year:
        params["dob_year"] = str(profile.dob_year)
    return params

def fetch_voters_from_fb_profiles(fb_profiles):
    voter_records = []
    for index in range(0, len(fb_profiles), 50):
        voter_records.extend(_fetch_voters_from_fb_profiles(
                fb_profiles[index:index+50]))
    return voter_records

def _fetch_voters_from_fb_profiles(fb_profiles):
    unfetched_both_steps = []
    voter_records = []
    for profile in fb_profiles:
        recs = VoterRecord.objects.filter(fb_uid=profile.uid)[:1]
        if len(recs) > 0:
            rec = recs[0]
            voter_records.append(rec)
        else:
            unfetched_both_steps.append(profile)
    unfetched_last_step = []
    while len(unfetched_both_steps) > 0 or len(unfetched_last_step) > 0:
        unfetched_both_steps, unfetched_last_step = \
            _fetch_voter_batch(
                unfetched_both_steps, 
                unfetched_last_step, 
                voter_records)
        if len(unfetched_both_steps) > 0 or len(unfetched_last_step) > 0:
            time.sleep(0.5 + random())
    return voter_records

def _relative_uri(profile, include_address):
    params = _params_from_fb_profile(profile, include_address)
    return _RELATIVE_URL + "?" + urlencode(
        dict([k, v.encode('utf-8')] for k, v in params.items()))

def _batch_post(request_list):
    if settings.USE_FAKE_VOTIZEN_API:
        elems = []
        for request in request_list:
            objects = []
            if choice([True, True, False]):
                objects = [ { "id": "".join([choice(string.letters) for i in range(10)]),
                              "is_registered_voter": choice([True, False]) } ]
            body = json.dumps({ "objects": objects })
            elems.append({ "body": body, "status_code": 200 })
        time.sleep(0.8)
        return 200, elems
    else:
        batch_url = _BATCH_URL + "?" + urlencode(
            { "api_key": settings.VOTIZEN_API_KEY,
              "format": "json"})
        response = requests.post(
            batch_url, 
            data={ "batch": json.dumps(request_list) })
        return response.status_code, response.json

def _fetch_profiles(profiles, include_address):
    request_list = [ { "method": "GET",
                       "relative_uri": _relative_uri(p, include_address) }
                     for p in profiles]
    status_code, voters = _batch_post(request_list)
    if status_code != 200:
        return profiles, [], []
    if len(request_list) > len(voters):
        logger.error(
            "posted {0} records to votizen but got {1} back".format(
                len(request_list), len(voters)))
    index = 0
    unfetched = []
    voter_records = []
    not_found = []
    for voter in voters:
        if voter['status_code'] == 200:
            body = json.loads(voter["body"])
            if "objects" in body and len(body["objects"]) > 0:
                obj = body["objects"][0]
                v = VoterRecord(
                    fb_uid=profiles[index].uid,
                    votizen_id=obj["id"],
                    registered=obj["is_registered_voter"])
                try:
                    v.save()
                    voter_records.append(v)
                except IntegrityError:
                    voter_records.append(VoterRecord.objects.get(fb_uid=profiles[index].uid))
            else:
                not_found.append(profiles[index])
        else:
            unfetched.append(profiles[index])
        index += 1
    return unfetched, voter_records, not_found

def _fetch_voter_batch(unfetched_both_steps, unfetched_last_step, voter_records):
    if len(unfetched_both_steps) > 0:
        unfetched_both_steps, new_voter_records, not_found_profiles = \
            _fetch_profiles(unfetched_both_steps, False)
        unfetched_last_step.extend(not_found_profiles)
        voter_records.extend(new_voter_records)
    if len(unfetched_last_step) > 0:
        unfetched_last_step, new_voter_records, not_found_profiles = \
            _fetch_profiles(unfetched_last_step, True)
        voter_records.extend(new_voter_records)
        for profile in not_found_profiles:
            v = VoterRecord(
                fb_uid=profile.uid,
                votizen_id="",
                registered=False)
            try:
                v.save()
                voter_records.append(v)
            except IntegrityError:
                voter_records.append(VoterRecord.objects.get(
                        fb_uid=profile.uid))
    return unfetched_both_steps, unfetched_last_step

def fetch_voter_from_fb_profile(fb_profile):
    fb_uid = fb_profile.uid
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
    votizen_id = "" if not voter else voter.id
    registered = False if not voter else voter.registered
    try:
        VoterRecord(fb_uid=fb_uid,
                    votizen_id=votizen_id,
                    registered=registered).save()
    except IntegrityError:
        pass
    return voter

def fetch_voter(**kwargs):
    if settings.USE_FAKE_VOTIZEN_API:
        time.sleep(0.3)
        if choice([True, True, False]):
            return Voter("".join([choice(string.letters) for i in range(10)]),
                         choice([True, False]))
        else:
            return None
    if not all(k in _FETCH_VOTER_PARAMS for k, v in kwargs.items()):
        raise AttributeError("Invalid arguments")
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
    else:
        try:
            VoterRecord(
                fb_uid=fb_uid,
                votizen_id="",
                registered=True).save()
        except IntegrityError:
            pass
