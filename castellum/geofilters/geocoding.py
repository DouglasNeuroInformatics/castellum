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

from geopy.geocoders import Nominatim

from castellum.contacts.models import Contact

from .models import Geolocation


def fetch_missing_geolocations():
    geolocator = Nominatim(user_agent="geofilter")
    geolocations = set()
    contacts = (
        Contact.objects
        .exclude(pk__in=Geolocation.objects.values('contact_id'))
        .select_related('address')
    )
    for contact in contacts:
        full_address = ' '.join([
            contact.address.street,
            contact.address.house_number,
            contact.address.zip_code,
            contact.address.city,
        ])

        resolved = geolocator.geocode(full_address)
        if resolved:
            geolocations.add(Geolocation(
                contact=contact,
                longitude=resolved.longitude,
                latitude=resolved.latitude,
            ))
    Geolocation.objects.bulk_create(geolocations)
