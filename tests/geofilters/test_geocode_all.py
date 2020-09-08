from collections import namedtuple
from unittest.mock import patch

from geopy.geocoders import Nominatim

from castellum.geofilters.management.commands.geocode_all import fetch_missing_geolocations

NOMINATIM = {'domain': 'localhost'}

Location = namedtuple('Location', ['longitude', 'latitude'])


@patch.object(Nominatim, 'geocode')
def test_fetch_missing_geolocations(geocode, settings, address):
    settings.NOMINATIM = NOMINATIM
    geocode.return_value = Location(0, 0)

    count = fetch_missing_geolocations()
    assert count == 1
    assert address.contact.geolocation
