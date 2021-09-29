"""Fetch SubjectCreationRequests from self registration.

Customize this script and copy it to ``castellum/subjects/management/commands/``,
You can then execute it using ``django-admin fetch_from_self_registration``.

See https://git.mpib-berlin.mpg.de/castellum/castellum_self_registration
"""

from django.core.management.base import BaseCommand
from django.forms import modelform_factory

import requests

from castellum.contacts.models import ContactCreationRequest
from castellum.subjects.models import SubjectCreationRequest

SubjectForm = modelform_factory(SubjectCreationRequest, fields=['delete_url'])
ContactForm = modelform_factory(ContactCreationRequest, fields=[
    'first_name', 'last_name', 'title', 'gender', 'date_of_birth', 'email'
])


def import_creationrequest(data, source):
    subject_form = SubjectForm(data)
    contact_form = ContactForm(data)

    subject_valid = subject_form.is_valid()
    contact_valid = contact_form.is_valid()

    if subject_valid and contact_valid:
        subject_form.instance.source = source
        subjectcreationrequest = subject_form.save()
        contact_form.instance.subject_id = subjectcreationrequest.pk
        contact_form.save()
        return subjectcreationrequest
    else:
        raise ValueError({**subject_form.errors, **contact_form.errors})


def do_import(url, token, source):
    r = requests.get(url, headers={'Authorization': 'token ' + token})
    r.raise_for_status()

    success = []
    errors = []

    for item in r.json()['subjects']:
        try:
            success.append(import_creationrequest(item, source))
        except Exception as e:
            errors.append(e)

    return success, errors


def do_cleanup_remote(token):
    success = []
    errors = []

    for subject in SubjectCreationRequest.objects.exclude(delete_url=None):
        r = requests.delete(subject.delete_url, headers={'Authorization': 'token ' + token})
        if r.status_code in [200, 204, 404]:
            subject.external_id = None
            subject.save()
            success.append(subject)
        else:
            errors.append(r)

    return success, errors


class Command(BaseCommand):
    help = __doc__.split('\n')[0]

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL to a list of subject creation requests (JSON)')
        parser.add_argument('--token', help='Authentication token')
        parser.add_argument('--source', help='Data source')

    def handle(self, *args, **options):
        success, errors = do_import(options['url'], options['token'], options['source'])
        if options['verbosity'] > 1:
            for error in errors:
                self.stderr.write(str(error))
        if options['verbosity'] > 0:
            self.stdout.write('Created {} subject creation requests'.format(len(success)))

        success, errors = do_cleanup_remote(options['token'])
        if options['verbosity'] > 1:
            for error in errors:
                self.stderr.write(str(error))
        if options['verbosity'] > 0:
            self.stdout.write(
                'Cleaned up {} subject creation requests from remote service'.format(len(success))
            )
