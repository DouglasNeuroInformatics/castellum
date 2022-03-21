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

import logging
from urllib.parse import quote_plus
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils import formats
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import requests
from dateutil.relativedelta import relativedelta
from icalevents import icalparser

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.models import Participation
from castellum.utils import add_working_days
from castellum.utils import cached_request
from castellum.utils import contrast_color
from castellum.utils import scheduler
from castellum.utils.mail import MailContext

from .models import Appointment

logger = logging.getLogger(__name__)


def date_format(dt):
    ldt = timezone.localtime(dt)
    return formats.date_format(ldt, 'l, ') + formats.date_format(ldt, 'DATETIME_FORMAT')


def get_reminder_body(name, session, dt):
    def get_mail_data():
        return {
            'name': name,
            'study': session.study.name,
            'date': date_format(dt),
            'reply_to': session.study.email,
            'session_reminder_text': session.reminder_text.strip() or '—',
        }

    return (
        get_mail_data,
        settings.CASTELLUM_APPOINTMENT_MAIL_BODY,
        settings.CASTELLUM_APPOINTMENT_MAIL_BODY_EN,
    )


def send_appointment_notifications(participation, changes, base_url, user=None):
    start = timezone.now()
    end = add_working_days(start, 2)
    relevant_changes = [
        (old, new) for (old, new) in changes if (
            (old and old >= start and old <= end) or
            (new and new >= start and new <= end)
        )
    ]

    if not relevant_changes:
        return

    def format_datetime(dt):
        if not dt:
            return _('not scheduled')
        return formats.date_format(timezone.localtime(dt), 'DATETIME_FORMAT')

    def get_mail_data():
        return {
            'study': participation.study,
            'changes': '\n'.join('{} -> {}'.format(
                format_datetime(old),
                format_datetime(new),
            ) for (old, new) in relevant_changes),
            'participation_url': urljoin(base_url, reverse(
                'execution:participation-detail',
                args=[participation.study.pk, participation.pk]
            )),
            'calendar_url': urljoin(base_url, reverse(
                'execution:calendar',
                args=[participation.study.pk]
            )),
        }

    recipients = [u.email for u in participation.study.conductors if u != user]
    if recipients:
        with MailContext('internal') as ctx:
            return ctx.send_mail(
                settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_SUBJECT,
                (
                    get_mail_data,
                    settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY,
                    settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY_EN,
                ),
                recipients,
                cc=[u.email for u in [user] if u],
            )


def get_external_resource_events(resource, start, end):
    if not resource.url:
        return []
    try:
        events = []
        url = (
            resource.url
            .replace('{start}', quote_plus(start.isoformat()))
            .replace('{end}', quote_plus(end.isoformat()))
        )
        text = cached_request(url, timeout=60)
        for event in icalparser.parse_events(text, start=start, end=end):
            events.append({
                'title': '[{}] {}'.format(resource, event.summary or ''),
                'start': event.start,
                'end': event.end,
                'backgroundColor': resource.color,
                'borderColor': resource.color,
                'textColor': contrast_color(resource.color),
            })
        return events
    except Exception as e:
        logger.error('Fetching events for resource {} failed: {}'.format(resource.pk, e))
        return []


def fetch_scheduler_appointments(study, base_url, timeout=0):
    count = 0
    now = timezone.now()

    for session in (
        study.studysession_set
        .exclude(schedule_id=None)
        .filter(schedule_updated_at__lt=now - relativedelta(seconds=timeout))
    ):
        try:
            data = scheduler.get_bulk(session.schedule_id)
        except requests.RequestException as e:
            logger.error('Fetching schedule for session {} failed: {}'.format(session.pk, e))
            continue

        session.schedule_updated_at = now
        session.save()

        for participation in session.study.participation_set.filter(status=Participation.INVITED):
            pseudonym = get_pseudonym(participation.subject, session.domain)
            start = data.get(pseudonym)

            change = Appointment.change_start(session, participation, start)
            if change:
                count += 1
                send_appointment_notifications(participation, [change], base_url)
    return count
