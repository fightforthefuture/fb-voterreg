import facebook
from main.models import User, Friendship

def fetch_friends(fb_uid, access_token):
    # this is a long-running function. so don't run it as part of an http request.
    graph = facebook.GraphAPI(access_token)
    friends = graph.get_connections("me", "friends")
    
