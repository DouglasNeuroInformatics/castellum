import pytest

from model_mommy import mommy
from castellum.contacts.models import City, Address, Contact


@pytest.fixture
def city():
    return mommy.make(City)


@pytest.fixture
def address():
    return mommy.make(Address)


@pytest.fixture
def contact(address):
    return mommy.make(Contact, address=address)


@pytest.fixture
def contact_data():
    return {
        'first_name': 'Winston',
        'last_name': 'Wolfe',
        'title': 'Dr.',
        'gender': 'm',
        'date_of_birth': '2010-01-28',
        'privacy_level': 0,
    }


@pytest.fixture
def address_data(address):
    return {
        'country': address.city.country.name,
        'city': address.city.name,
        'zip_code': address.zip_code,
        'street': address.street,
        'house_number': address.house_number,
        'additional_information': address.additional_information,
    }


@pytest.fixture
def full_data(contact_data, address_data):
    contact_data.update(address_data)
    return contact_data
