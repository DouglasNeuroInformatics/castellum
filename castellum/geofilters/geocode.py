# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
        logger.info(
            f'Geocoding failed for subject with pk "{address.contact.subject.pk}"'
        )
        return None
