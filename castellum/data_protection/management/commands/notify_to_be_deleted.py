# (c) 2018
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
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.urls import reverse

from castellum.data_protection import helpers
from castellum.studies.models import Study
from castellum.subjects.models import Subject


def studies_notify(studies, base_url):
    count = 0
    for study in studies:
        if not study.to_be_deleted_notified:
            study.to_be_deleted_notified = True
            study.save()
            count += 1

            url = base_url + reverse('studies:detail', args=[study.pk])
            send_mail(
                settings.CASTELLUM_DELETE_NOTIFICATION_SUBJECT,
                settings.CASTELLUM_DELETE_NOTIFICATION_BODY.format(url=url),
                settings.DEFAULT_FROM_EMAIL,
                [settings.CASTELLUM_DELETE_NOTIFICATION_TO],
            )
    print('notified about %i studies' % count)


def studies_reset(studies):
    count = 0
    for study in Study.objects.filter(to_be_deleted_notified=True):
        if study not in studies:
            study.to_be_deleted_notified = False
            study.save()
            count += 1
    print('reset %i studies that previously were marked as notified' % count)


def studies_handle(base_url, limit_by, **options):
    studies, missing = helpers.get_studies(limit_by)
    studies_notify(studies, base_url)
    if missing:
        print('skipped resetting because %i studies were missing' % missing)
    else:
        studies_reset(studies)
    print()


def subjects_notify(subjects, base_url):
    count = 0
    for subject in subjects:
        if not subject.to_be_deleted_notified:
            subject.to_be_deleted_notified = True
            subject.save()
            count += 1

            url = base_url + reverse('subjects:detail', args=[subject.pk])
            send_mail(
                settings.CASTELLUM_DELETE_NOTIFICATION_SUBJECT,
                settings.CASTELLUM_DELETE_NOTIFICATION_BODY.format(url=url),
                settings.DEFAULT_FROM_EMAIL,
                [settings.CASTELLUM_DELETE_NOTIFICATION_TO],
            )
    print('notified about %i subjects' % count)


def subjects_reset(subjects):
    count = 0
    for subject in Subject.objects.filter(to_be_deleted_notified=True):
        if subject not in subjects:
            subject.to_be_deleted_notified = False
            subject.save()
            count += 1
    print('reset %i subjects that previously were marked as notified' % count)


def subjects_handle(base_url, limit_by, **options):
    subjects, missing = helpers.get_all_subjects(limit_by)
    subjects_notify(subjects, base_url)
    if missing:
        print('skipped resetting because %i subjects were missing' % missing)
    else:
        subjects_reset(subjects)
    print()


class Command(BaseCommand):
    help = 'Automatically notify about content that should be deleted.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')
        parser.add_argument('--limit-by', default=100, type=int)

    def handle(self, *args, **options):
        if not settings.CASTELLUM_DELETE_NOTIFICATION_TO:
            raise CommandError('CASTELLUM_DELETE_NOTIFICATION_TO is not set')

        studies_handle(**options)
        subjects_handle(**options)
