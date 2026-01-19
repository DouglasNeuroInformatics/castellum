# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from castellum.studies.models import Study
from castellum.studies.models import StudySession
from castellum.utils import scheduler


class Command(BaseCommand):
    help = 'Automatically clear old schedules and session domains.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--dry-run', action='store_true')
        parser.add_argument('-m', '--months', type=int, default=12)

    def handle(self, *args, **options):
        threshold = timezone.now() - relativedelta(months=options['months'])

        qs = StudySession.objects.annotate(
            a=models.Max('appointment__start')
        ).filter(
            models.Q(a__isnull=True) | models.Q(a__lt=threshold),
            study__status=Study.FINISHED,
            study__updated_at__lt=threshold.date(),
        )

        if options['dry_run']:
            for session in qs:
                self.stdout.write(session.pk)
        else:
            n = qs.count()
            for session in qs:
                session.domains.all().delete()
                if session.schedule_id:
                    if settings.SCHEDULER_URL:
                        scheduler.delete_schedule(session.schedule_id)
                    session.schedule_id = None
                    session.save()

            if options['verbosity'] > 0:
                self.stdout.write(f'cleaned {n} sessions')
