from django.core.management.base import BaseCommand, CommandError
from main import models
from voterapi.models import VoterRecord

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
        friend_fbuids = [u.fb_uid for u in user.friendship_set.all()]
        user_vbs = user.votingblock_set.all().values_list('id', flat=True)
        models.VotingBlockMember.objects.filter(id__in=user_vbs).delete()
        models.VotingBlockFriendship.objects.filter(voting_block_id__in=user_vbs).delete()
        user.votingblockmember_set.all().delete()
        user.votingblock_set.all().delete()
        user.friendship_set.all().delete()
        user.friendshipbatch_set.all().delete()
        user.mission_set.all().delete()
        user.delete()
        if len(args) > 1 and args[1] == "y":
            for fb_uid in friend_fbuids:
                VoterRecord.objects.filter(fb_uid=fb_uid).delete()
