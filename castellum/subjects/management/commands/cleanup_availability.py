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
from django.utils import timezone

from castellum.subjects.models import Subject


class Command(BaseCommand):
    help = 'Remove obsolete "not available until" entries.'

    def handle(self, *args, **options):
        now = timezone.now()
        subjects = Subject.objects.filter(not_available_until__lt=now)
        count = subjects.update(not_available_until=None)
        if options['verbosity'] > 0 and count > 0:
            self.stdout.write('Cleared {} "not available until" entries'.format(count))
