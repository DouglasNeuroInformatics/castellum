# (c) 2018-2020
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

import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import formats
from django.utils import timezone

from castellum.recruitment.models import Appointment
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.utils.mail import get_context
from castellum.utils.mail import send_mail

logger = logging.getLogger(__name__)


def send_mail_to_subject(study, appointment, reply_to):
    contact = appointment.participation.subject.contact
    if not contact.own_or_guardian_email:
        return False

    try:
        return send_mail(
            settings.CASTELLUM_APPOINTMENT_MAIL_SUBJECT,
            settings.CASTELLUM_APPOINTMENT_MAIL_BODY.format(
                subject=contact.full_name,
                study=study.name,
                date=formats.date_format(appointment.start, 'DATETIME_FORMAT'),
                reply_to=reply_to,
            ),
            [contact.own_or_guardian_email],
            reply_to=[reply_to],
            context='recruitment',
        )
    except ValueError:
        logger.debug('Failed to send email to subject %i', contact.subject.pk)
        return False


def send_mail_to_study_conductors(study, not_reachable, base_url):
    urls = '\n'.join(
        base_url + reverse(
            'execution:participation-detail',
            args=[study.pk, appointment.participation.pk],
        )
        for appointment in not_reachable
    )
    send_mail(
        settings.CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_SUBJECT.format(study=study),
        settings.CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY.format(urls=urls),
        [user.email for user in study.study_conductors],
        context='internal',
    )


def send_appointment_reminders(base_url):
    now = timezone.now()
    reached_count = 0
    not_reached_count = 0

    for study in Study.objects.filter(status=Study.EXECUTION):
        due_appointments = Appointment.objects.filter(
            start__gte=now,
            start__lte=now + settings.CASTELLUM_APPOINTMENT_REMINDER_PERIOD,
            reminded=False,
            session__study=study,
            participation__status=Participation.INVITED,
        ).select_related('participation__subject')
        not_reachable = []
        recruitment_mail = get_context('recruitment')['from_email']
        reply_to = (
            study.mail_reply_address
            or recruitment_mail
            or settings.DEFAULT_FROM_EMAIL
        )

        for appointment in due_appointments:
            success = send_mail_to_subject(study, appointment, reply_to)
            if success:
                reached_count += 1
            else:
                not_reached_count += 1
                not_reachable.append(appointment)

        if not_reachable:
            send_mail_to_study_conductors(study, not_reachable, base_url)

        due_appointments.update(reminded=True)

    print('Direct: {}'.format(reached_count))
    print('Indirect: {}'.format(not_reached_count))


class Command(BaseCommand):
    help = 'Remind subjects of due appointments.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        send_appointment_reminders(options['base_url'])
