import pytest

from model_mommy import mommy

from subject_management.models import Address


@pytest.fixture
def address():
    return mommy.make(Address)
