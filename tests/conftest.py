from django.db.models import DateField
from django.utils import timezone

import pytest
from model_mommy import mommy

from castellum.castellum_auth.models import User
from castellum.contacts.models import Contact
from castellum.studies.models import Study

mommy.generators.add(
    'castellum.utils.fields.DateField', mommy.generators.default_mapping[DateField])


@pytest.fixture
def user(db):
    future = timezone.now() + timezone.timedelta(days=10000)
    return User.objects.create(expiration_date=future, is_superuser=True)


@pytest.fixture
def study(db):
    return mommy.make(Study)


@pytest.fixture
def published_study(db):
    return mommy.make(Study, published=True)


@pytest.fixture
def unpublished_study(db):
    return mommy.make(Study, published=False)


@pytest.fixture
def contact(db):
    return mommy.make(Contact, pseudonym=None)
