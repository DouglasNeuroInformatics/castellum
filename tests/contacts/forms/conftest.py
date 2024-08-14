import pytest
from model_bakery import baker

from castellum.contacts.models import Address
from castellum.contacts.models import Contact


@pytest.fixture
def address():
    return baker.make(Address)


@pytest.fixture
def contact(address):
    return baker.make(Contact, address=address)


@pytest.fixture
def contact_data():
    return {
        'first_name': 'Winston',
        'last_name': 'Wolfe',
        'title': 'Dr.',
        'date_of_birth': '1910-01-28',
    }


@pytest.fixture
def address_data(address):
    return {
        'country': address.country,
        'city': address.city,
        'zip_code': address.zip_code,
        'street': address.street,
        'house_number': address.house_number,
        'additional_information': address.additional_information,
    }


@pytest.fixture
def full_data(contact_data, address_data):
    contact_data.update(address_data)
    return contact_data
