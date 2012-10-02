from django.core.management.base import BaseCommand, CommandError
from main import models

class Command(BaseCommand):
    def handle(self, *args, **options):
        name = args[0]
        try:
            user = models.User.objects.get(name=name)
        except models.User.DoesNotExist:
            print("No user named {0} found".format(name))
            return
        proceed = raw_input(
            "This will clear all info for {0}. Sure? (y/n) ".format(name))
        if proceed != "y":
            return
        user.friendship_set.all().delete()
        user.friendshipbatch_set.all().delete()
        user.delete()
