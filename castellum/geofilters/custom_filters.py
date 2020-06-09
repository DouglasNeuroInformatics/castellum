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

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models

from castellum.recruitment import filter_registry

from .geocoding import fetch_missing_geolocations
from .models import Geolocation


@filter_registry.register('dummy_geo_filter')
def dummy_geo_filter(**kwargs):
    fetch_missing_geolocations()

    center = Point(52.4685095, 13.3037248)
    locations = Geolocation.objects.filter(point__distance_lt=(center, D(km=3)))
    pks = locations.values_list('contact__subject_id', flat=True)
    return models.Q(pk__in=list(pks))
