from celery import task
import fb_friends

@task()
def fetch_fb_friends(fb_uid, access_token):
    return fb_friends.fetch_friends(fb_uid, access_token)

@task()
def update_friends_of(user_id, access_token):
    fb_friends.update_friends_of(user_id, access_token)
