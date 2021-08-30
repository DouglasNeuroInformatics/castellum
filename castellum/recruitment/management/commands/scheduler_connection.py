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

import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

import requests

from castellum.appointments.mixins import send_appointment_notifications
from castellum.appointments.models import Appointment
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.models import Participation
from castellum.studies.models import StudySession
from castellum.utils import scheduler


def event_source(*args, **kwargs):
    # https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
    while True:
        r = requests.get(*args, stream=True, **kwargs)
        r.raise_for_status()
        message = {}
        for line in r.iter_lines(decode_unicode=True, chunk_size=1):
            if not line:
                if message:
                    yield message
                message = {}
            elif line.startswith(':'):
                pass
            else:
                if ':' in line:
                    key, value = line.split(': ', 1)
                else:
                    key, value = line, ''
                message[key] = value.lstrip()


class Command(BaseCommand):
    help = 'Subscribe to and handle scheduler events.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def update_appointment(self, schedule_id, pseudonym, base_url):
        session = get_object_or_404(StudySession, schedule_id=schedule_id)
        subject = get_subject(session.domain, pseudonym)
        participation = Participation.objects.get(subject=subject, study=session.study)

        old = Appointment.objects.filter(participation=participation, session=session).first()
        new_start = scheduler.get(schedule_id, pseudonym)

        if old:
            if not new_start:
                changes = [(old.start, None)]
                old.delete()
            elif new_start != old.start:
                changes = [(old.start, new_start)]
                old.start = new_start
                old.reminded = False
                old.save()
        elif new_start:
            changes = [(None, new_start)]
            participation.appointment_set.create(
                session=session,
                start=new_start,
            )

        send_appointment_notifications(participation, changes, base_url)

    def handle(self, *args, **options):
        headers = {'Authorization': 'token ' + settings.SCHEDULER_TOKEN}
        url = settings.SCHEDULER_URL + '/api/events/'

        for event in event_source(url, headers=headers):
            data = json.loads(event['data'])
            status = 'success'

            try:
                self.update_appointment(data['schedule'], data['token'], options['base_url'])
            except Exception:
                status = 'error'

            requests.post('{}?id={}&{}'.format(url, event['id'], status), headers=headers)
