# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.management.base import BaseCommand
from django.utils import timezone

from castellum.subjects.models import Subject


class Command(BaseCommand):
    help = 'Remove obsolete "not available until" entries.'

    def handle(self, *args, **options):
        now = timezone.now()
        subjects = Subject.objects.filter(not_available_until__lt=now)
        count = subjects.update(not_available_until=None)
        if options['verbosity'] > 0:
            self.stdout.write(f'Cleared {count} "not available until" entries')
