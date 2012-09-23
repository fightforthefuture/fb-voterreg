import requests
from django.conf import settings
from models import VoterRecord, APIHitCount
import facebook
from django.db import IntegrityError

MAX_API_HITS = 100000

_STATE_ABBREVIATIONS = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

_STATES = dict((v, k) for k, v in _STATE_ABBREVIATIONS.items())

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
    params = {
        "first_name": fb_profile["first_name"],
        "last_name": fb_profile["last_name"] }
    location = fb_profile.get("location", None)
    birthday = fb_profile.get("birthday", None)
    if include_address and location and location["name"]:
        parts = location["name"].split(", ")
        if len(parts) == 2 and parts[1] in _STATES:
            params["city"] = parts[0]
            params["state"] = _STATES[parts[1]]
    if birthday:
        parts = birthday.split("/")
        params["dob_month"] = int(parts[0])
        params["dob_day"] = int(parts[1])
        if len(parts) > 2:
            params["dob_year"] = int(parts[2])
    return params

def fetch_voter_from_fb_uid(uid, access_token):
    graph = facebook.GraphAPI(access_token)
    return fetch_voter_from_fb_profile(graph.get_object(uid))

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
        return None
    if not all(k in _FETCH_VOTER_PARAMS for k, v in kwargs.items()):
        raise AttributeError("Invalid arguments")
    hit_count = APIHitCount.next()
    if hit_count > MAX_API_HITS:
        return None
    params = kwargs.copy()
    params["api_key"] = settings.VOTIZEN_API_KEY
    response = requests.get(_URL, params=params).json
    if len(response["objects"]) > 0:
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
