# (c) 2018-2020
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

from geopy.distance import distance

from castellum.geofilters.models import Geolocation

from ...models import ExampleResult


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        center = (52.4685095, 13.3037248)
        results = []
        for loc in Geolocation.objects:
            d = distance((loc.lat, loc.lng), center)
            results.append(ExampleResult(
                subject_id=loc.contact.subject_id,
                is_match=d.km < 3,
            ))
        ExampleResult.objects.bulk_create(results)
        print('Create %i results' % len(results))
