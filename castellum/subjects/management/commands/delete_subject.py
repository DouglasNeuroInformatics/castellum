from django.core.management.base import BaseCommand

from castellum.contacts.models import Contact


class Command(BaseCommand):
    help = 'Delete a subject with all of their data.'

    def add_arguments(self, parser):
        parser.add_argument('first_name')
        parser.add_argument('last_name')

    def handle(self, *args, **options):
        contact = Contact.objects.get(
            first_name=options['first_name'],
            last_name=options['last_name'],
        )

        contact.delete_full()
