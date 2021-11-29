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

from django.core.management.base import BaseCommand

from castellum.appointments.helpers import send_appointment_notifications
from castellum.appointments.models import Appointment
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.studies.models import StudySession
from castellum.utils import scheduler


class Command(BaseCommand):
    help = 'Fetch appointments from scheduler.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        count = 0

        for session in (
            StudySession.objects
            .filter(study__status=Study.EXECUTION)
            .exclude(schedule_id=None)
        ):
            data = scheduler.get_bulk(session.schedule_id)

            for participation in session.study.participation_set.filter(
                status=Participation.INVITED
            ):
                pseudonym = get_pseudonym(participation.subject, session.domain)
                start = data.get(pseudonym)

                changes = Appointment.change_start(session, participation, start)
                if changes:
                    count += 1
                    send_appointment_notifications(participation, changes, options['base_url'])

        if options['verbosity'] > 0:
            self.stdout.write('Updated {} appointments'.format(count))
