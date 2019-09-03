import pytest
from model_mommy import mommy

from castellum.contacts.models import Address
from castellum.contacts.models import City
from castellum.contacts.models import Contact


@pytest.fixture
def city():
    return mommy.make(City)


@pytest.fixture
def address():
    return mommy.make(Address)


@pytest.fixture
def contact(address, contact_domain):
    return mommy.make(Contact, address=address, pseudonym=None)


@pytest.fixture
def contact_data():
    return {
        'first_name': 'Winston',
        'last_name': 'Wolfe',
        'title': 'Dr.',
        'gender': 'm',
        'date_of_birth': '1910-01-28',
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
