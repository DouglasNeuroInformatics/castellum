# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.conf import settings
from django.contrib.gis.geos import Point

from . import geocode


def invalidate_geolocation(address, update=False):
    from .models import Geolocation

    # The geocoding might fail, so we should delete the outdated
    # data in any case.
    Geolocation.objects.filter(contact=address.contact).delete()

    if update and hasattr(settings, 'NOMINATIM'):
        geocoded = geocode.geocode_address(address)
        if geocoded:
            Geolocation.objects.create(
                contact_id=address.contact_id,
                point=Point(geocoded.longitude, geocoded.latitude),
            )


def delete_geolocation_on_address_change(sender, instance=None, **kwargs):
    from castellum.contacts.models import Address

    if sender is Address:
        invalidate_geolocation(instance)


def geocode_on_address_change(sender, instance=None, **kwargs):
    from castellum.contacts.models import Address

    if sender is Address:
        invalidate_geolocation(instance, update=True)
