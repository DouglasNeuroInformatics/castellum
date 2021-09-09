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

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.urls import reverse

from castellum.data_protection import helpers
from castellum.subjects.models import Subject
from castellum.utils.mail import MailContext


def subjects_notify(subjects, base_url):
    count = 0
    with MailContext('internal') as ctx:
        for subject in subjects.filter(to_be_deleted_notified=False):
            url = base_url + reverse('subjects:detail', args=[subject.slug])
            sent = ctx.send_mail(
                settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_SUBJECT,
                (
                    lambda: {'url': url},
                    settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY,
                    settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY_EN,
                ),
                settings.CASTELLUM_GDPR_NOTIFICATION_TO,
            )
            if sent:
                count += 1
                subject.to_be_deleted_notified = True
                subject.save()
    return count


def subjects_reset(subjects):
    count = 0
    for subject in Subject.objects.filter(to_be_deleted_notified=True):
        if subject not in subjects:
            subject.to_be_deleted_notified = False
            subject.save()
            count += 1
    return count


class Command(BaseCommand):
    help = 'Automatically notify about subjects that should be deleted.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        if not settings.CASTELLUM_GDPR_NOTIFICATION_TO:
            raise CommandError('CASTELLUM_GDPR_NOTIFICATION_TO is not set')

        subjects = helpers.get_all_subjects()

        count = subjects_notify(subjects, options['base_url'])
        if options['verbosity'] > 0:
            self.stdout.write(
                'notify to be deleted: '
                'notifications about {} subjects have been sent'.format(count)
            )

        count = subjects_reset(subjects)
        if options['verbosity'] > 0:
            self.stdout.write(
                'notify to be deleted: '
                'reset {} subjects that previously were marked as notified'.format(count)
            )
