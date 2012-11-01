from django.conf import settings
from models import VoterRecord, VoterHistoryRecord
from fb_utils import FacebookProfile
from django.db import IntegrityError
from random import choice, random
from urllib import urlencode
from datetime import date
import re
import requests
import json
import facebook
import time
import string
import logging

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
        new_voter_records = _fetch_voters_from_fb_profiles(
            fb_profiles[index:index+50])
        voter_records.extend(new_voter_records)
    return voter_records

def fill_voter_history(voter_records):
    fetchable = [v for v in voter_records if 
                 v.votizen_id and not v.loaded_history]
    for index in range(0, len(fetchable), 50):
        _fill_voter_history(fetchable[index:index+50])

def _fill_voter_history(voter_records):
    unfilled_records = voter_records
    while len(unfilled_records) > 0:
        request_list = \
            [ { "method": "GET",
                "relative_uri": 
                    "/v1/voter/{0}/record/?format=json".format(v.votizen_id) }
              for v in unfilled_records]
        status_code, objects = _batch_history_post(request_list)
        if status_code != 200:
            continue
        index = 0
        current_unfilled = []
        for obj in objects:
            voter_record = unfilled_records[index]
            index += 1
            if obj["status_code"] == 200:
                voter_record = VoterRecord.objects.get(id=voter_record.id)
                body = json.loads(obj["body"])
                if body["id"] != voter_record.votizen_id:
                    raise Exception("bad response from votizen")
                history_records = \
                    [_create_voter_history_record(voter_record, j)
                     for j in body["voting_history"]]
                voter_record.loaded_history = True
                voter_record.save()
                _update_user_and_friendship(
                    voter_record.fb_uid, history_records)
            else:
                current_unfilled.append(voter_record)
        unfilled_records = current_unfilled

def _voting_frequency(start_year, votes):
    from main import models as main_models
    if (start_year % 4) != 0:
        start_year += (4 - (start_year % 4))
    num_voted = 0
    num_not_voted = 0
    for year in range(start_year, 2011, 4):
        if year in votes:
            if votes[year]:
                num_voted += 1
            else:
                num_not_voted += 1
        else:
            num_not_voted += 1
    if num_not_voted == 0 and num_voted > 0:
        return main_models.VOTING_FREQUENCY_ALWAYS
    elif num_not_voted < num_voted:
        return main_models.VOTING_FREQUENCY_SOMETIMES
    else:
        return main_models.VOTING_FREQUENCY_RARELY

def _update_user_and_friendship(fb_uid, voter_history_records):
    from main.models import User, Friendship, VOTING_FREQUENCY_RARELY
    votes = dict([(v.date.year, v.voted) for v in voter_history_records if
                  v.date.year % 4 == 0])
    dates_voted = [v.date for v in voter_history_records if v.voted]
    last_voted = None if len(dates_voted) == 0 else max(dates_voted)
    u = None
    if len(dates_voted) > 0:
        recs = User.objects.filter(fb_uid=fb_uid)
        u = None if len(recs) == 0 else recs[0]
        recs = Friendship.objects.filter(fb_uid=fb_uid)[:1]
        f = None if len(recs) == 0 else recs[0]
        birthday = None
        if u and u.birthday:
            birthday = u.birthday
        if not birthday and f and f.birthday:
            birthday = f.birthday
        if birthday:
            voting_frequency = _voting_frequency(
                birthday.year + 19, votes)
        else:
            voting_frequency = _voting_frequency(
                min([v.date.year for v in voter_history_records]), votes)
    else:
        voting_frequency = VOTING_FREQUENCY_RARELY
    User.objects.filter(fb_uid=fb_uid).update(
        voting_frequency=voting_frequency,
        last_voted=last_voted)
    Friendship.objects.filter(fb_uid=fb_uid).update(
        voting_frequency=voting_frequency,
        last_voted=last_voted)

def _create_voter_history_record(voter_record, json_record):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", json_record["date"])
    voting_date = date(*[int(m.group(i)) for i in range(1, 4)])
    recs = VoterHistoryRecord.objects.filter(
        voter=voter_record, date=voting_date)[:1]
    if len(recs) == 0:
        vhr = VoterHistoryRecord(
            voter=voter_record,
            date=voting_date,
            voted=(json_record["voted"].lower() == "yes"))
        vhr.save()
        return vhr
    else:
        return recs[0]

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

def _batch_history_post(request_list):
    if settings.USE_FAKE_VOTIZEN_API:
        elems = []
        for request in request_list:
            votizen_id = re.search(
                r"voter/([^/]+)/record", request["relative_uri"]).group(1)
            voting_history = []
            for year in range(2000, 2010, 4):
                voting_history.append(
                    { "date": "{0}-11-06".format(year),
                      "voted": choice(["Yes", "No"]) })
            body = json.dumps({"id": votizen_id, "voting_history": voting_history})
            elems.append({ "status_code": 200, "body": body })
        return 200, elems
    else:
        batch_url = _BATCH_URL + "?" + urlencode(
            { "api_key": settings.VOTIZEN_API_KEY,
              "format": "json" })
        response = requests.post(
            batch_url, 
            data={ "batch": json.dumps(request_list) })
        return response.status_code, response.json

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
    fill_voter_history(voter_records)
    return unfetched, voter_records, not_found

def _fetch_voter_batch(unfetched_both_steps, unfetched_last_step, voter_records):
    starting_len = len(unfetched_both_steps) + \
        len(unfetched_last_step) + \
        len(voter_records)
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
    if not VoterRecord.objects.filter(fb_uid=fb_uid).exists():
        try:
            v = VoterRecord(fb_uid=fb_uid,
                        votizen_id=votizen_id,
                        registered=registered)
            v.save()
        except IntegrityError:
            pass
    else:
        v = VoterRecord.objects.get(fb_uid=fb_uid)
    fill_voter_history([v])
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
