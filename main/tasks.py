from celery import task
import fb_friends

@task()
def fetch_fb_friends(fb_uid, access_token):
    return fb_friends.fetch_friends(fb_uid, access_token)

@task()
def update_friends_of(user_id):
    fb_friends.update_friends_of(user_id)

@task()
def send_notification(notification_id):
    from models import LastAppNotification
    notification = LastAppNotification.objects.get(id=notification_id)
    notification.send()
