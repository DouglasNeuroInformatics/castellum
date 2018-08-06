import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact


@pytest.fixture
def contact(db):
    return mommy.make(Contact, pseudonym=None)
