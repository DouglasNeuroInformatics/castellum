from django.contrib.auth.models import Permission
from django.db.models import DateField
from django.utils import timezone

import pytest
from model_mommy import mommy

from castellum.castellum_auth.models import User
from castellum.contacts.models import Contact
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership

mommy.generators.add(
    'castellum.utils.fields.DateField', mommy.generators.default_mapping[DateField])


@pytest.fixture
def user(db):
    future = timezone.now() + timezone.timedelta(days=10000)
    user = User.objects.create(expiration_date=future)
    user.user_permissions.set(Permission.objects.all())
    user.user_permissions.remove(Permission.objects.get(codename='privacy_level_2'))
    return user


@pytest.fixture
def admin(user):
    user.is_staff = True
    user.save()
    return user


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
def member(user, study, published_study, unpublished_study):
    StudyMembership.objects.create(user=user, study=study)
    StudyMembership.objects.create(user=user, study=published_study)
    StudyMembership.objects.create(user=user, study=unpublished_study)
    return user


@pytest.fixture
def contact(db):
    return mommy.make(Contact, pseudonym=None, privacy_level=0)
