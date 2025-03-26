# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from castellum.contacts.models import Address
from castellum.geofilters.geocode import geocode_address
from castellum.geofilters.models import Geolocation


def fetch_missing_geolocations(limit=None):
    geolocations = []
    addresses = Address.objects.filter(contact__geolocation=None)
    for address in addresses[:limit]:
        geocoded = geocode_address(address)
        if geocoded:
            geolocations.append(Geolocation(
                contact_id=address.contact_id,
                point=Point(geocoded.longitude, geocoded.latitude),
            ))
    Geolocation.objects.bulk_create(geolocations)

    return len(geolocations)


class Command(BaseCommand):
    help = 'Fetch missing geolocations.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)

    def handle(self, *args, **options):
        if not hasattr(settings, 'NOMINATIM'):
            raise CommandError('NOMINATIM not configured')
        count = fetch_missing_geolocations(options['limit'])
        if options['verbosity'] > 0:
            self.stdout.write(f'Created {count} geolocations')
