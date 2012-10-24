from django.db import models
from django.db.models import F

class VoterRecord(models.Model):
    fb_uid = models.CharField(max_length=32, unique=True)
    votizen_id = models.CharField(max_length=32)
    registered = models.BooleanField()
