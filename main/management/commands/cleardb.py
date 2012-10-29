from django.core.management.base import BaseCommand, CommandError
from main import models

class Command(BaseCommand):
    def handle(self, *args, **options):
        proceed = raw_input("This will clear all tables. Sure? (y/n) ")
        if proceed != "y":
            return
        models.VotingBlockFriendship.objects.all().delete()
        models.VotingBlockMember.objects.all().delete()
        models.VotingBlock.objects.all().delete()
        models.Friendship.objects.all().delete()
        models.FriendshipBatch.objects.all().delete()
        models.Mission.objects.all().delete()
        models.User.objects.all().delete()
