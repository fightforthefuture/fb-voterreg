from datetime import datetime

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet


class FriendQuerySet(QuerySet):

    prefiltered = False

    def _years_ago(self, years, from_date=None):
        """
        Leap-year sensitive way of determining a date X years ago, patching
        datetime.timedelta's lack of support for a years argument.
        """
        if from_date is None:
            from_date = datetime.now()
        try:
            return from_date.replace(year=from_date.year - years)

        # Must be a leap day; let's return 2/28 of that year
        except ValueError:
            return from_date.replace(
                month=2,
                day=28,
                year=from_date.year - years
            )

    def all(self):
        """
        Prefilters all users matching the following criteria:
        - User is younger than 18 years old on 11/06/2012

        Also keeps track of whether this operation has already been run on
        this QuerySet instance, ensuring that the SQL clauses aren't duplicated
        when the query is executed.
        """
        all_friends = super(FriendQuerySet, self).all()

        if not self.prefiltered:
            election_day = datetime(year=2012, month=11, day=6)
            eligibility_date = self._years_ago(18, election_day)
            all_friends = all_friends.filter(
                Q(birthday__isnull=True) |
                Q(birthday__lte=eligibility_date)
            )
            self.prefiltered = True

        return all_friends

    def registered(self, status=True):
        return self.all().filter(registered=status)

    def pledged(self, status=True):
        return self.all().filter(date_pledged__isnull=not status)

    def invited(self, status=True):
        if status:
            return self.all().filter(
                Q(invited_with_batch=True) | Q(invited_individually=True)
            )
        else:
            return self.all().filter(
                Q(invited_with_batch=False) & Q(invited_individually=False)
            )

    def invited_not_pledged(self):
        return self.invited().filter(date_pledged__isnull=True)

    def voted(self, status=True):
        return self.all().filter(date_voted__isnull=not status)

    def personally_invited(self, status=True):
        return self.all().filter(invited_individually=status)

    def batch_invited(self, status=True):
        return self.all().filter(invited_with_batch=status)


class FriendStatusManager(models.Manager):

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def get_query_set(self):
        return FriendQuerySet(self.model).all()
