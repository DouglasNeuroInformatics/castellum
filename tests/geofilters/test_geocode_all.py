from collections import namedtuple
from unittest.mock import patch

from geopy.geocoders import Nominatim
from model_bakery import baker

from castellum.contacts.models import Address
from castellum.geofilters.management.commands.geocode_all import (
    fetch_missing_geolocations,
)

NOMINATIM = {'domain': 'localhost'}

Location = namedtuple('Location', ['longitude', 'latitude'])


@patch.object(Nominatim, 'geocode')
def test_fetch_missing_geolocations(geocode, settings, address):
    settings.NOMINATIM = NOMINATIM
    geocode.return_value = Location(0, 0)

    count = fetch_missing_geolocations()
    assert count == 1
    assert address.contact.geolocation


@patch.object(Nominatim, 'geocode')
def test_fetch_missing_geolocations_limit(geocode, settings, db):
    baker.make(Address, _quantity=5)
    settings.NOMINATIM = NOMINATIM
    geocode.return_value = Location(0, 0)

    count = fetch_missing_geolocations(limit=2)
    assert count == 2
