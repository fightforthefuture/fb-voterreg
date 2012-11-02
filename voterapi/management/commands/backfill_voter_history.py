from django.core.management.base import BaseCommand, CommandError
from voterapi.models import VoterRecord, VoterHistoryRecord
from voterapi import fill_voter_history
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args, **options):
        chunk_no = 0
        count = VoterRecord.objects.filter(
            loaded_history=False).filter(~Q(votizen_id="")).count()
        print("backfilling for {0}".format(count))
        for start_index in range(0, count, 50):
            print("On chunk {0}".format(chunk_no))
            chunk = VoterRecord.objects.\
                filter(loaded_history=False).filter(~Q(votizen_id="")).order_by("id")[start_index:start_index+50]
            fill_voter_history(chunk)
            chunk_no += 1
