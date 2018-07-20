import pytest

from model_mommy import mommy
from subject_management.models import City, Address, Subject


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
