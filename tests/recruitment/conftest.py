import pytest
from model_mommy import mommy

from castellum.studies.models import Study
from castellum.contacts.models import Contact


@pytest.fixture
def study(db):
    return mommy.make(Study)


@pytest.fixture
def contact(db):
    return mommy.make(Contact, pseudonym=None)
