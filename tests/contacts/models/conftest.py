import pytest

from castellum.contacts.models import Address
from castellum.contacts.models import City
from castellum.contacts.models import Country


@pytest.fixture
def country():
    return Country(name="Germany")


@pytest.fixture
def city(country):
    return City(name="Berlin", country=country)


@pytest.fixture
def address(city):
    return Address(city=city, zip_code="10787", street="Hardenbergplatz", house_number="8",
                   additional_information="")
