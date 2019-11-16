import pytest

from castellum.contacts.models import Address


@pytest.fixture
def address():
    return Address(
        country='Germany',
        city='Berlin',
        zip_code='10787',
        street='Hardenbergplatz',
        house_number='8',
        additional_information='',
    )
