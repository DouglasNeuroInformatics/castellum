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

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from geopy.geocoders import Nominatim

from castellum.contacts.models import Contact
from castellum.geofilters.models import Geolocation


def fetch_missing_geolocations():
    geolocator = Nominatim(**settings.NOMINATIM)
    geolocations = []
    contacts = (
        Contact.objects
        .exclude(pk__in=Geolocation.objects.values('contact_id'))
        .select_related('address')
    )
    for contact in contacts:
        resolved = geolocator.geocode({
            'street': ' '.join([
                contact.address.street,
                contact.address.house_number,
            ]),
            'city': contact.address.city,
            'country': contact.address.country,
            'postalcode': contact.address.zip_code,
        })
        if resolved:
            geolocations.append(Geolocation(
                contact=contact,
                point=Point(resolved.longitude, resolved.latitude),
            ))
    Geolocation.objects.bulk_create(geolocations)

    print('Created %i geolocations' % len(geolocations))


class Command(BaseCommand):
    help = 'Fetch missing geolocations.'

    def handle(self, *args, **options):
        fetch_missing_geolocations()
