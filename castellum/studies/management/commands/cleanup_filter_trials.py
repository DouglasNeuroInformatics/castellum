# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.management.base import BaseCommand

from castellum.studies.models import Study


class Command(BaseCommand):
    help = 'Delete filter trials'

    def handle(self, *args, **options):
        Study.objects.filter(is_filter_trial=True).delete()
