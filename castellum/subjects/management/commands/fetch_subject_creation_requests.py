# (c) 2018-2021
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

"""
Depending on the service that is used to gather SubjectCreationRequests
this script may not be flexible enough. In that case it can still serve
as an example.
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


def import_creationrequest(data):
    subject_form = SubjectForm(data)
    contact_form = ContactForm(data)

    subject_valid = subject_form.is_valid()
    contact_valid = contact_form.is_valid()

    if subject_valid and contact_valid:
        subjectcreationrequest = subject_form.save()
        contact_form.instance.subject_id = subjectcreationrequest.pk
        contact_form.save()
        return subjectcreationrequest
    else:
        raise ValueError({**subject_form.errors, **contact_form.errors})


def do_import(url, token):
    r = requests.get(url, headers={'Authorization': 'token ' + token})
    r.raise_for_status()

    success = []
    errors = []

    for item in r.json()['subjects']:
        try:
            success.append(import_creationrequest(item))
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
    help = 'Fetch SubjectCreationRequests from an external service.'

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL to a list of subject creation requests (JSON)')
        parser.add_argument('--token', help='Authentication token')

    def handle(self, *args, **options):
        success, errors = do_import(options['url'], options['token'])
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
