from datetime import date

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

def _location_parts(location):
    if location and location.get("name", False):
        parts = location["name"].split(", ")
        if len(parts) == 2 and parts[1] in _STATES:
            return parts[0], _STATES[parts[1]]
    return None, None

class FacebookProfile(object):
    def __init__(self, profile):
        if "id" in profile:
            self._init_from_profile(profile)
        else:
            self._init_from_fql(profile)

    def _init_from_fql(self, record):
        self.uid = record["uid"]
        location = record.get("current_location", None) or {}
        self.location = location.get("name", None)
        self.location_city = location.get("city", None)
        self.location_state = \
            _STATES.get(location.get("state", "none"), None)
        location = record.get("hometown_location", None) or {}
        self.hometown_city = location.get("city", None)
        self.hometown_state = \
            _STATES.get(location.get("state", "none"), None)
        self._init(record)

    def _init_from_profile(self, profile):
        self.uid = profile["id"]
        location = profile.get("location", None)
        if location and location.get("name", False):
            self.location = location.get("name")
        else:
            self.location = None
        self.location_city, self.location_state = \
            _location_parts(location)
        self.hometown_city, self.hometown_state = \
            _location_parts(profile.get("hometown", None))
        self._init(profile)

    def _init(self, profile):
        self.name = profile["name"]
        self.first_name = profile["first_name"]
        self.last_name = profile["last_name"]
        self.dob_month = None
        self.dob_day = None
        self.dob_year = None
        self.dob = None
        birthday = profile.get("birthday", profile.get("birthday_date", None))
        if birthday:
            parts = birthday.split("/")
            self.dob_month = int(parts[0])
            self.dob_day = int(parts[1])
            if len(parts) > 2:
                self.dob_year = int(parts[2])
                self.dob = date(int(parts[2]),
                                self.dob_month, 
                                self.dob_day)

    def far_from_home(self):
        return self.location_state is not None and \
            self.hometown_state is not None and \
            self.location_state != self.hometown_state


def opengraph_url(request, action):
    return 'https://graph.facebook.com/%s/%s' % (
        request.facebook["uid"],
        action,
    )
