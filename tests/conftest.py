from django.contrib.auth.models import Permission
from django.db.models import DateField
from django.utils import timezone

import pytest
from model_mommy import mommy

from castellum.castellum_auth.models import User
from castellum.contacts.models import Contact
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership
from castellum.castellum_auth.sample_data import GROUPS

mommy.generators.add(
    'castellum.utils.fields.DateField', mommy.generators.default_mapping[DateField])


def create_user(codenames):
    future = timezone.now() + timezone.timedelta(days=10000)
    user = User.objects.create(expiration_date=future)

    perms = Permission.objects.all()
    if codenames:
        perms = perms.filter(codename__in=codenames)
    user.user_permissions.set(perms)

    user.user_permissions.add(Permission.objects.get(codename='privacy_level_1'))
    user.user_permissions.remove(Permission.objects.get(codename='privacy_level_2'))

    return user


@pytest.fixture
def user(db):
    return create_user([])


@pytest.fixture
def study_coordinator(db):
    return create_user(GROUPS['Study coordinator'])


@pytest.fixture
def subject_manager(db):
    return create_user(GROUPS['Subject manager'])


@pytest.fixture
def recruiter(db):
    return create_user(GROUPS['Subject manager'])


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
