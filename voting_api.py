class Voter(object):
    @property
    def registered(self):
        return False

def requests_exhausted():
    return False

def fetch_voter(fb_uid, access_token):
    return Voter()
