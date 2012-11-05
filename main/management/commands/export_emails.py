import csv
import datetime
from optparse import make_option
import time

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from main.models import User, VotingBlock


class Command(BaseCommand):
    """

    """
    args = '<VotingBlock ID>'
    help = (
        'Returns the URL of a CSV containing names and email addresses of '
        'all users in the Voting Block of the passed ID. If no voting '
        'block is selected, returns information of all users.'
    )
    option_list = BaseCommand.option_list + (
        make_option('--block',
            action='store',
            type='int',
            dest='block',
            default=None,
            help='ID of the voting block'
        ),
    )

    def handle(self, *args, **options):
        if options['block']:
            block = VotingBlock.objects.get(pk=options['block'])
            users = User.objects.filter(votingblockmember__voting_block=block)
            prefix = slugify(block.name)
        else:
            users = User.objects.all()
            prefix = 'all'

        headers = [
            ['First Name(supporter)', 'Last Name(supporter)', 'Email(supporter)']
        ]
        user_list = [
            [user.first_name, user.last_name, user.email] for user in users
        ]
        filename = ('%s_%s.csv' % (
            prefix,
            int(time.mktime(datetime.datetime.now().timetuple())),
        ))[:32]

        csv_file = ContentFile(render_to_string('csv.txt', {
            'data': headers + user_list
        }))
        path = default_storage.save('exports/' + filename, csv_file)
        self.stdout.write('Export available at %s%s\n' % (
            settings.MEDIA_URL,
            path,
        ))
