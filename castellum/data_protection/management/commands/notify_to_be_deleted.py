# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
            url = urljoin(base_url, reverse('subjects:detail', args=[subject.pk]))
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
                Subject.objects.filter(pk=subject.pk).update(
                    to_be_deleted_notified=True
                )
    return count


def subjects_reset(subjects):
    return (
        Subject.objects
        .filter(to_be_deleted_notified=True)
        .exclude(pk__in=subjects)
        .update(to_be_deleted_notified=False)
    )


class Command(BaseCommand):
    help = 'Automatically notify about subjects that should be deleted.'

    def handle(self, *args, **options):
        if not settings.CASTELLUM_GDPR_NOTIFICATION_TO:
            raise CommandError('CASTELLUM_GDPR_NOTIFICATION_TO is not set')

        subjects = helpers.get_subjects().exclude(
            to_be_deleted__isnull=True,
            no_legal_basis=False,
            unreachable=False,
        )

        count = subjects_notify(subjects, settings.CASTELLUM_EMAIL_BASE_URL)
        if options['verbosity'] > 0:
            self.stdout.write(
                'notify to be deleted: '
                f'notifications about {count} subjects have been sent'
            )

        count = subjects_reset(subjects)
        if options['verbosity'] > 0:
            self.stdout.write(
                'notify to be deleted: '
                f'reset {count} subjects that previously were marked as notified'
            )
