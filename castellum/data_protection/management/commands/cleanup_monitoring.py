# (c) 2018
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

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from castellum.data_protection.models import MonitoringEntry


def parse_timedelta(s):
    days = int(s)
    return timedelta(days=days)


class Command(BaseCommand):
    help = 'Delete expired monitoring entries.'

    def add_arguments(self, parser):
        if not settings.CASTELLUM_MONITORING_ENTRY_DELETION_PERIOD:
            raise CommandError('CASTELLUM_MONITORING_ENTRY_DELETION_PERIOD is not set')
        parser.add_argument(
            '--deletion-period',
            default=settings.CASTELLUM_MONITORING_ENTRY_DELETION_PERIOD,
            type=parse_timedelta,
            help=_(
                    'Delete all monitoring entries older than DAYS days. By default,'
                    'CASTELLUM_MONITORING_ENTRY_DELETION_PERIOD from the Castellum settings '
                    'will be used.'
                ),
            metavar='DAYS',
        )

    def handle(self, *args, **options):
        acceptable_datetime = timezone.now() - options['deletion_period']
        entries = MonitoringEntry.objects.filter(date__lte=acceptable_datetime)
        count, __ = entries.delete()
        print('Deleted %i entries' % count)
