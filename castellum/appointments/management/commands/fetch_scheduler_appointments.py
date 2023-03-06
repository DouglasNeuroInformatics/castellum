# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.core.management.base import BaseCommand

from castellum.appointments.helpers import fetch_scheduler_appointments
from castellum.studies.models import Study
from castellum.studies.models import StudySession


class Command(BaseCommand):
    help = 'Fetch appointments from scheduler.'

    def add_arguments(self, parser):
        parser.add_argument('base_url')

    def handle(self, *args, **options):
        count = 0
        for study in Study.objects.filter(
            status=Study.EXECUTION,
            pk__in=StudySession.objects.exclude(schedule_id=None).values('study'),
        ):
            count += fetch_scheduler_appointments(study, options['base_url'])

        if options['verbosity'] > 0:
            self.stdout.write(f'Updated {count} appointments')
