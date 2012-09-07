from celery import task
import fb_friends

@task()
def fetch_fb_friends(fb_uid, access_token):
    return fb_friends.fetch_friends(fb_uid, access_token)
