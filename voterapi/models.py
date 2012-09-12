from django.db import models
from django.db.models import F

class VoterRecord(models.Model):
    fb_uid = models.CharField(max_length=32, unique=True)
    votizen_id = models.CharField(max_length=32)
    registered = models.BooleanField()

class APIHitCount(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    count = models.IntegerField(default=0)

    @classmethod
    def next(cls):
        KEY = "default"
        try:
            cls.objects.filter(pk=KEY).update(count=F("count") + 1)
            return cls.objects.get(pk=KEY).count
        except cls.DoesNotExist:
            return cls.objects.create(key=KEY, count=1).count
