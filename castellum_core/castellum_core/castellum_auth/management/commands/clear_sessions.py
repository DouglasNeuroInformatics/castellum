from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    help = 'Delete all sessions, logging out all users'

    def handle(self, *args, **options):
        count, __ = Session.objects.all().delete()
        self.stdout.write('Deleted {} sessions'.format(count))
