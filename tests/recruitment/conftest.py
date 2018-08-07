from django.conf import settings

import pytest
from model_mommy import mommy

from castellum.studies.models import Study
from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.recruitment.models import AttributeSet


@pytest.fixture
def study(db):
    return mommy.make(Study)


@pytest.fixture
def contact(db):
    return mommy.make(Contact, pseudonym=None)


@pytest.fixture
def attributeset(contact):
    pseudonym = resolve_pseudonym(
        settings.DOMAINS['contact'], contact.pseudonym, settings.DOMAINS['attributeset'])
    return mommy.make(AttributeSet, pseudonym=pseudonym)
