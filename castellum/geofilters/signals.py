# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete

from castellum.contacts.models import Address

from . import geocode
from .models import Geolocation


def invalidate_geolocation(address, update=False):
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
    if sender is Address:
        invalidate_geolocation(instance)


def geocode_on_address_change(sender, instance=None, **kwargs):
    if sender is Address:
        invalidate_geolocation(instance, update=True)


def register_signal_handlers():
    pre_delete.connect(delete_geolocation_on_address_change)
    post_save.connect(geocode_on_address_change)
