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

from django.db import models

from geopy.geocoders import Nominatim

from castellum.contacts.models import Contact
from castellum.recruitment import filter_registry

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


@filter_registry.register('dummy_geo_filter')
def dummy_geo_filter(**kwargs):
    fetch_missing_geolocations()

    locations = Geolocation.objects.select_related('contact')
    filtered = set()
    for loc in locations:
        # this is an example query. It doesn't do anything sensible.
        if loc.longitude == 0 and loc.latitude == 0:
            filtered.add(loc.contact.pk)
    return models.Q(data__d1='foo', pk__in=filtered)


    
