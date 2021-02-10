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

import logging

from django.conf import settings

from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


def geocode_address(address):
    query = {
        'street': ' '.join([
            address.street,
            address.house_number,
        ]),
        'city': address.city,
        'country': address.country,
        'postalcode': address.zip_code,
    }
    try:
        geolocator = Nominatim(**settings.NOMINATIM)
        return geolocator.geocode(query)
    except GeopyError:
        logger.info(f'Geocoding failed for subject with pk "{address.contact.subject_id}"')
        return None
