import datetime
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core import serializers
from django.db.models import DateField
from django.test import TestCase
from django.utils import timezone

import pytest
from model_mommy import mommy

from castellum.castellum_auth.models import User
from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import get_subject
from castellum.pseudonyms.models import Domain
from castellum.recruitment.management.commands import create_sample_attribute_descriptions
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership

mommy.generators.add(
    'castellum.utils.fields.DateField', mommy.generators.default_mapping[DateField])

# monkey patch to make test isolation work on both databases
# See https://github.com/pytest-dev/pytest-django/pull/431
TestCase.databases = ('default', 'contacts')


def load_django_fixture(app_label, name):
    path = os.path.join('castellum', app_label, 'fixtures', name + '.json')
    with open(path) as fh:
        for obj in serializers.deserialize('json', fh):
            obj.save()


def create_user(group_name):
    future = timezone.now() + datetime.timedelta(days=10000)
    user = User.objects.create(expiration_date=future)

    if group_name:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
    else:
        user.user_permissions.set(Permission.objects.all())

    user.user_permissions.add(Permission.objects.get(codename='privacy_level_1'))
    user.user_permissions.remove(Permission.objects.get(codename='privacy_level_2'))

    return user


@pytest.fixture(scope='session', autouse=True)
def contact_domain(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        data = settings.CASTELLUM_DOMAINS['contact']
        domain, __ = Domain.objects.get_or_create(key=data['key'], defaults=data)
        return domain


@pytest.fixture(scope='session', autouse=True)
def attribute_descriptions(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        create_sample_attribute_descriptions.generate_attribute_descriptions()


@pytest.fixture(scope='session', autouse=True)
def sample_groups(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        load_django_fixture('castellum_auth', 'sample_groups')


@pytest.fixture(scope='session', autouse=True)
def study_types(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        load_django_fixture('studies', 'study_types')


@pytest.fixture
def user(db):
    return create_user(None)


@pytest.fixture
def study_conductor(db):
    return create_user('Study conductor')


@pytest.fixture
def study_coordinator(db):
    return create_user('Study coordinator')


@pytest.fixture
def subject_manager(db):
    return create_user('Subject manager')


@pytest.fixture
def recruiter(db):
    return create_user('Recruiter')


@pytest.fixture
def data_protection_officer(db):
    return create_user('Data protection officer')


@pytest.fixture
def admin(user):
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def study(db):
    return mommy.make(Study)


@pytest.fixture
def study_in_execution_mode(db):
    return mommy.make(Study, study_mode=Study.EXECUTION)


@pytest.fixture
def study_in_edit_mode(db):
    return mommy.make(Study, study_mode=Study.EDIT)


@pytest.fixture
def member(user, study, study_in_execution_mode, study_in_edit_mode):
    StudyMembership.objects.create(user=user, study=study)
    StudyMembership.objects.create(user=user, study=study_in_execution_mode)
    StudyMembership.objects.create(user=user, study=study_in_edit_mode)
    return user


@pytest.fixture
def contact(db, contact_domain):
    return mommy.make(Contact)


@pytest.fixture
def attributeset(contact, contact_domain):
    subject = get_subject(contact_domain.key, contact.pseudonym)
    return mommy.make(AttributeSet, subject=subject)


@pytest.fixture
def participation_request(contact, study_in_execution_mode, contact_domain):
    subject = get_subject(contact_domain.key, contact.pseudonym)
    return mommy.make(ParticipationRequest, study=study_in_execution_mode, subject=subject)


@pytest.fixture
def attribute_description(db, attribute_descriptions):
    return AttributeDescription.objects.get(pk=1)


@pytest.fixture
def subject_filter_group(db, study_in_edit_mode):
    return mommy.make(SubjectFilterGroup, study=study_in_edit_mode)


@pytest.fixture
def subject_filter(subject_filter_group, attribute_description):
    return SubjectFilter.objects.create(
        description=attribute_description,
        operator='exact',
        value='left',
        group=subject_filter_group)
