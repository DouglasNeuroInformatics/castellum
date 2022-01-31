# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

from urllib.parse import urljoin

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
            url = urljoin(base_url, reverse('subjects:detail', args=[subject.uuid]))
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
                # do not set updated_at
                Subject.objects.filter(pk=subject.pk).update(to_be_deleted_notified=True)
    return count


def subjects_reset(subjects):
    return (
        Subject.objects
        .filter(to_be_deleted_notified=True)
        .update(to_be_deleted_notified=False)
    )


class Command(BaseCommand):
    help = 'Automatically notify about subjects that should be deleted.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        if not settings.CASTELLUM_GDPR_NOTIFICATION_TO:
            raise CommandError('CASTELLUM_GDPR_NOTIFICATION_TO is not set')

        subjects = helpers.get_subjects().exclude(
            to_be_deleted__isnull=True,
            no_legal_basis=False,
            unreachable=False,
        )

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
