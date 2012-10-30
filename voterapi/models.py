from django.db import models
from django.db.models import F

class VoterRecord(models.Model):
    fb_uid = models.CharField(max_length=32, unique=True)
    votizen_id = models.CharField(max_length=32)
    registered = models.BooleanField()
    loaded_history = models.BooleanField(default=False)

class VoterHistoryRecord(models.Model):
    class Meta:
        unique_together = ("voter", "date",)
    voter = models.ForeignKey(VoterRecord)
    date = models.DateField()
    voted = models.BooleanField()
