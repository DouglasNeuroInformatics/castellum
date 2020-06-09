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

import requests

from castellum.contacts.models import Contact

from .models import Geolocation

NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'


def geocode(address):
    query = {
        'country': address.country,
        'city': address.city,
        'street': '%s %s' % (address.street, address.house_number),
        'limit': 1,
        'format': 'json',
    }
    try:
        r = requests.get(NOMINATIM_URL, query)
        r.raise_for_status()
        data = r.json()
        return float(data[0]['lat']), float(data[0]['lon'])
    except:
        # FIXME: error handling
        pass


def fetch_missing_geolocations():
    geolocations = set()
    contacts = (
        Contact.objects
        .exclude(pk__in=Geolocation.objects.values('contact_id'))
        .select_related('address')
    )
    for contact in contacts:
        resolved = geocode(contact.address)
        if resolved:
            geolocations.add(Geolocation(
                contact=contact,
                longitude=resolved[0],
                latitude=resolved[1],
            ))
    Geolocation.objects.bulk_create(geolocations)
