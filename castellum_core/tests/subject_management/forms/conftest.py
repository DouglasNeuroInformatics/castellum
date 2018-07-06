import pytest

from model_mommy import mommy

from subject_management.models import Address


@pytest.fixture
def address():
    return mommy.make(Address)


@pytest.fixture
def stable_data():
    d = {
        'first_name': 'a',
        'last_name': 't',
        'title': 'Dr.',
        'gender': 'm',
        'birthday': '2010-01-28',
        'phone_number_alternative': '+4917691233435'
    }
    return d
