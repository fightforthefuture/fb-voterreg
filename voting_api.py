class Voter(object):
    def __init__(self, registered=False):
        self.registered = registered

def _requests_exhausted():
    return False

def fetch_voter(fb_uid, access_token):
    # if this gets hit with the same fb_uid as before,
    # it retrieves from db instead of hitting API again.
    # if requests are exhausted and this hits api, it will just say
    # the voter's not registered, harumph.
    return Voter()

def correct_voter(fb_uid):
    # TODO: this corrects the voter registration record, setting them to registered.
    pass
