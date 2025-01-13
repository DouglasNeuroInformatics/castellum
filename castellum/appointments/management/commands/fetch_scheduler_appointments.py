# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.core.management.base import BaseCommand

from castellum.appointments.helpers import fetch_scheduler_appointments
from castellum.studies.models import Study
from castellum.studies.models import StudySession


class Command(BaseCommand):
    help = 'Fetch appointments from scheduler.'

    def handle(self, *args, **options):
        count = 0
        for study in Study.objects.filter(
            status=Study.EXECUTION,
            pk__in=StudySession.objects.exclude(schedule_id=None).values('study'),
        ):
            count += fetch_scheduler_appointments(
                study, settings.CASTELLUM_EMAIL_BASE_URL
            )

        if options['verbosity'] > 0:
            self.stdout.write(f'Updated {count} appointments')
