"""Fetch SubjectCreationRequests from self registration.

You can save a lot of work by allowing subjects to sign up for the
recruitment by themselves. However, this can easily lead to low quality
entries (duplicates, missing data, spam, …). So castellum provides an
intermediary step: Subjects can create a SubjectCreationRequest, and
subject managers can review those requests and convert them to proper
subject entries with just a few clicks.

Since Castellum is not meant to be accessible from the internet for
security reasons, it does not provide a UI for subjects to create those
SubjectCreationRequest themselves. Instead, a script is needed to import
the SubjectCreationRequest from an external source, e.g. a survey tool.

This script show how that could be done.
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


def get_remote_data(url, token):
    r = requests.get(url, headers={'Authorization': f'token {token}'})
    r.raise_for_status()
    return r.json()['subjects']


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


def do_import(items, source):
    success = []
    errors = []

    for item in items:
        if SubjectCreationRequest.objects.filter(delete_url=item['delete_url']).exists():
            continue
        try:
            success.append(import_creationrequest(item, source))
        except Exception as e:
            errors.append(e)

    return success, errors


def do_cleanup_local(items):
    count, _ = (
        SubjectCreationRequest.objects
        .filter(is_deleted=True)
        .exclude(delete_url__in=[item['delete_url'] for item in items])
        .delete()
    )
    return count


def do_cleanup_remote(token):
    success = []
    errors = []

    for subject in SubjectCreationRequest.objects.exclude(delete_url=None):
        r = requests.delete(subject.delete_url, headers={
            'Authorization': f'token {token}'
        })
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
        parser.add_argument('--delete', action='store_true')

    def log(self, msg, errors, options):
        if options['verbosity'] > 1:
            for error in errors:
                self.stderr.write(str(error))
        if options['verbosity'] > 0:
            self.stdout.write(msg)

    def handle(self, *args, **options):
        items = get_remote_data(options['url'], options['token'])

        success, errors = do_import(items, options['source'])
        self.log(f'Created {len(success)} subject creation requests', errors, options)

        success_count = do_cleanup_local(items)
        self.log(f'Cleaned up {success_count} local subject creation requests', [], options)

        if options['delete']:
            success, errors = do_cleanup_remote(options['token'])
            msg = f'Cleaned up {len(success)} subject creation requests from remote service'
            self.log(msg, errors, options)
