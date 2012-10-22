from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet


class FriendQuerySet(QuerySet):

    def registered(self, status=True):
        return self.filter(registered=status)

    def pledged(self, status=True):
        return self.filter(date_pledged__isnull=not status)

    def invited(self, status=True):
        if status:
            return self.filter(
                Q(invited_with_batch=True) | Q(invited_individually=True)
            )
        else:
            return self.filter(
                Q(invited_with_batch=False) & Q(invited_individually=False)
            )

    def invited_not_pledged(self):
        return self.invited().filter(date_pledged__isnull=True)

    def voted(self, status=True):
        return self.filter(date_voted__isnull=not status)

    def personally_invited(self, status=True):
        return self.filter(invited_individually=status)

    def batch_invited(self, status=True):
        return self.filter(invited_with_batch=status)


class FriendStatusManager(models.Manager):

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def get_query_set(self):
        return FriendQuerySet(self.model)
