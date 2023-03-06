from collections import namedtuple
from unittest.mock import patch

from django.contrib.gis.geos import Point
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim
from model_bakery import baker

from castellum.contacts.models import Address
from castellum.geofilters.models import Geolocation

NOMINATIM = {'domain': 'localhost'}

Location = namedtuple('Location', ['longitude', 'latitude'])


@patch.object(Nominatim, 'geocode')
def test_geocode_on_create(geocode, settings, db):
    settings.NOMINATIM = NOMINATIM
    geocode.return_value = Location(0, 0)
    baker.make(Address)
    assert Geolocation.objects.exists()
    assert Geolocation.objects.get().point.tuple == (0, 0)


@patch.object(Nominatim, 'geocode')
def test_geocode_on_update(geocode, settings, address):
    settings.NOMINATIM = NOMINATIM
    geocode.return_value = Location(1, 1)
    address.city = 'foo'
    address.save()
    assert Geolocation.objects.exists()
    assert Geolocation.objects.get().point.tuple == (1, 1)


def test_cleanup_on_delete(address):
    baker.make(Geolocation, contact=address.contact, point=Point(0, 0))
    assert Geolocation.objects.exists()

    address.delete()
    assert not Geolocation.objects.exists()


@patch.object(Nominatim, 'geocode')
def test_cleanup_on_empty(geocode, settings, address):
    settings.NOMINATIM = NOMINATIM
    baker.make(Geolocation, contact=address.contact, point=Point(0, 0))
    assert Geolocation.objects.exists()

    geocode.return_value = None
    address.city = 'foo'
    address.save()
    assert not Geolocation.objects.exists()


@patch.object(Nominatim, 'geocode')
def test_cleanup_on_exception(geocode, settings, address):
    settings.NOMINATIM = NOMINATIM
    baker.make(Geolocation, contact=address.contact, point=Point(0, 0))
    assert Geolocation.objects.exists()

    geocode.side_effect = GeopyError
    address.city = 'foo'
    address.save()
    assert not Geolocation.objects.exists()
