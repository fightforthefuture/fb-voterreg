from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

class User(models.Model):
    fb_uid = models.CharField(max_length=32, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    registered = models.BooleanField(default=False)
    used_registration_widget = models.BooleanField(default=False)
    date_pledged = models.DateTimeField(null=True)
    date_invited_friends = models.DateTimeField(null=True)
    # number of invited friends who have pledged
    invited_pledge_count = models.IntegerField(default=0)
    # whether or not my data has been fetched from the votizen api.
    data_fetched = models.BooleanField(default=False)
    friends_fetch_started = models.BooleanField(default=False)
    # whether or not we've filled in Friendship models for this user yet.
    friends_fetched = models.BooleanField(default=False)

    @property
    def pledged(self):
        return self.date_pledged is not None

    @property
    def invited_friends(self):
        return self.date_invited_friends is not None

    def is_admirable(self):
        return self.registered or self.pledged or self.invited_friends

class Friendship(models.Model):
    class Meta:
        unique_together = (("user", "friend",),)
    user = models.ForeignKey(User, related_name="friends")
    user_fb_uid = models.CharField(max_length=32, db_index=True)
    friend = models.ForeignKey(User, related_name="friends_of")
    friend_fb_uid = models.CharField(max_length=32, db_index=True)
    # registered * 1 + pledged * 1
    display_ordering = models.IntegerField(default=0, db_index=True)
    registered = models.BooleanField()
    date_pledged = models.DateTimeField(null=True)
    invited_pledge_count = models.IntegerField(default=0)

    @property
    def pledged(self):
        return self.date_pledged is not None

    def picture_url(self):
        return "https://graph.facebook.com/{0}/picture?type=large".format(
            self.user_fb_uid)

@receiver(pre_save, sender=Friendship)
def fill_in_display_ordering(sender, **kwargs):
    sender.display_ordering = \
        (1 if sender.registered else 0) + \
        (1 if sender.pledged else 0)
