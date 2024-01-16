# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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

import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from castellum.appointments.helpers import get_reminder_body
from castellum.studies.models import Study
from castellum.utils.mail import MailContext


def send_mail_to_subject(ctx, study, appointment):
    contact = appointment.participation.subject.contact
    return ctx.send_separate_mails(
        settings.CASTELLUM_APPOINTMENT_MAIL_SUBJECT,
        get_reminder_body(contact.full_name, appointment.session, appointment.start),
        contact.own_or_legal_representative_emails,
        reply_to=[study.email],
        recipients_string=contact.email_recipients_string,
    )


def send_batch(ctx, study, appointments, state):
    not_reachable = []
    for appointment in appointments.select_related('participation__subject'):
        try:
            success = send_mail_to_subject(ctx, study, appointment)
        except Exception:
            success = False
        if success:
            state['reached_count'] += 1
        else:
            state['not_reached_count'] += 1
            not_reachable.append(appointment)
    return not_reachable


def send_mail_to_study_conductors(study, not_reachable, base_url, ctx):
    urls = '\n'.join(
        urljoin(base_url, reverse(
            'execution:participation-detail',
            args=[study.pk, appointment.participation.pk],
        ))
        for appointment in not_reachable
    )
    return ctx.send_mail(
        settings.CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_SUBJECT.format(study=study),
        (
            lambda: {'urls': urls},
            settings.CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY,
            settings.CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY_EN,
        ),
        [user.email for user in study.conductors],
    )


def send_appointment_reminders(base_url):
    now = timezone.now()
    state = {
        'reached_count': 0,
        'not_reached_count': 0,
    }

    with MailContext('recruitment') as ctx:
        for study in Study.objects.filter(status=Study.EXECUTION):
            not_reachable = []

            for session in study.studysession_set.all():
                if session.second_reminder_days:
                    appointments = session.appointment_set.filter(
                        start__gte=now,
                        start__lte=(
                            now + datetime.timedelta(days=session.second_reminder_days)
                        ),
                        first_reminder_sent=True,
                        second_reminder_sent=False,
                    )
                    not_reachable += send_batch(ctx, study, appointments, state)
                    appointments.update(second_reminder_sent=True)

                if session.first_reminder_days:
                    appointments = session.appointment_set.filter(
                        start__gte=now,
                        start__lte=(
                            now + datetime.timedelta(days=session.first_reminder_days)
                        ),
                        first_reminder_sent=False,
                    )
                    not_reachable += send_batch(ctx, study, appointments, state)
                    appointments.update(first_reminder_sent=True)

        if not_reachable:
            with MailContext('internal', ctx.connection) as internal_ctx:
                send_mail_to_study_conductors(
                    study, not_reachable, base_url, internal_ctx
                )

    return state['reached_count'], state['not_reached_count']


class Command(BaseCommand):
    help = 'Remind subjects of due appointments.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        reached_count, not_reached_count = send_appointment_reminders(
            options['base_url']
        )
        if options['verbosity'] > 0:
            self.stdout.write(f'Direct appointment reminders: {reached_count}')
            self.stdout.write(f'Indirect appointment reminders: {not_reached_count}')
