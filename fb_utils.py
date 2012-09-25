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
        self.first_name = profile["first_name"]
        self.last_name = profile["last_name"]
        location = profile.get("location", None)
        if location and location.get("name", False):
            self.location = location.get("name")
        else:
            self.location = None
        self.location_city, self.location_state = \
            _location_parts(location)
        self.hometown_city, self.hometown_state = \
            _location_parts(profile.get("hometown", None))
        self.dob_month = None
        self.dob_day = None
        self.dob_year = None
        self.dob = None
        birthday = profile.get("birthday", None)        
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
        return self.location_state and \
            self.hometown_state and \
            self.location_state != self.hometown_state
