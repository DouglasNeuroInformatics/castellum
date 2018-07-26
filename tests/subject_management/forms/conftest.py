import pytest

from model_mommy import mommy
from castellum.subject_management.models import City, Address, Subject


@pytest.fixture
def city():
    return mommy.make(City)


@pytest.fixture
def address():
    return mommy.make(Address)


@pytest.fixture
def subject(address):
    return mommy.make(Subject, address=address)


@pytest.fixture
def subject_data():
    return {
        'first_name': 'Winston',
        'last_name': 'Wolfe',
        'title': 'Dr.',
        'gender': 'm',
        'birthday': '2010-01-28',
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
def full_data(subject_data, address_data):
    subject_data.update(address_data)
    return subject_data
