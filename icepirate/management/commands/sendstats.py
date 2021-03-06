import sys

from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from group.models import Group
from member.models import Member

from icepirate.utils import quick_mail

class Command(BaseCommand):

    def handle(self, *args, **options):

        groups = Group.objects.all()
        for group in groups:
            subject = 'Statistics for group "%s"' % group.name
            body = []

            body.append('These are the member statistics for the group "%s"' % group.name)
            body.append('Member count: %d' % group.members.count())

            sys.stdout.write('Sending member statistics for group \'%s\'...' % group.techname)
            quick_mail(group.email, subject, '\n'.join(body))
            sys.stdout.write(' done\n')


