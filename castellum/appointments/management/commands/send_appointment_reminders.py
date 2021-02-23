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

import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from castellum.appointments.helpers import get_reminder_body
from castellum.appointments.models import Appointment
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.utils.mail import MailContext

logger = logging.getLogger(__name__)


def send_mail_to_subject(ctx, study, appointment):
    contact = appointment.participation.subject.contact
    return ctx.send_separate_mails(
        settings.CASTELLUM_APPOINTMENT_MAIL_SUBJECT,
        get_reminder_body(contact.full_name, appointment.session, appointment.start),
        contact.own_or_guardian_emails,
        reply_to=[study.email],
        recipients_string=contact.email_recipients_string,
    )


def send_mail_to_study_conductors(study, not_reachable, base_url):
    urls = '\n'.join(
        base_url + reverse(
            'execution:participation-detail',
            args=[study.pk, appointment.participation.pk],
        )
        for appointment in not_reachable
    )
    with MailContext('internal') as ctx:
        return ctx.send_mail(
            settings.CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_SUBJECT.format(study=study),
            settings.CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY.format(urls=urls),
            [user.email for user in study.conductors],
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

        with MailContext('recruitment') as ctx:
            for appointment in due_appointments:
                success = send_mail_to_subject(ctx, study, appointment)
                if success:
                    reached_count += 1
                else:
                    not_reached_count += 1
                    not_reachable.append(appointment)

        if not_reachable:
            send_mail_to_study_conductors(study, not_reachable, base_url)

        due_appointments.update(reminded=True)

    return reached_count, not_reached_count


class Command(BaseCommand):
    help = 'Remind subjects of due appointments.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        reached_count, not_reached_count = send_appointment_reminders(options['base_url'])
        if options['verbosity'] > 0:
            self.stdout.write('Direct: {}'.format(reached_count))
            self.stdout.write('Indirect: {}'.format(not_reached_count))
