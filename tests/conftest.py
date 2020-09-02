import datetime
import os

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.postgres.fields import JSONField as PostgresJSONField
from django.core import serializers
from django.db.models import DateField
from django.db.models import DateTimeField
from django.db.models import JSONField
from django.test import TestCase
from django.utils import timezone

import pytest
from model_bakery import baker

from castellum.castellum_auth.models import User
from castellum.contacts.models import Address
from castellum.contacts.models import Contact
from castellum.recruitment.management.commands import create_attribute_descriptions
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership

baker.generators.add(
    'castellum.utils.fields.DateField', baker.generators.default_mapping[DateField]
)
baker.generators.add(
    'castellum.utils.fields.DateTimeField', baker.generators.default_mapping[DateTimeField]
)
baker.generators.add(
    JSONField, baker.generators.default_mapping[PostgresJSONField]
)

# monkey patch to make test isolation work on both databases
# See https://github.com/pytest-dev/pytest-django/pull/431
TestCase.databases = ['default', 'contacts']


def load_django_fixture(app_label, name):
    path = os.path.join('castellum', app_label, 'fixtures', name + '.json')
    with open(path) as fh:
        for obj in serializers.deserialize('json', fh):
            obj.save()


def create_user(group_name):
    future = timezone.now() + datetime.timedelta(days=10000)
    user = baker.make(User, expiration_date=future, email='test@example.com')

    if group_name:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
    else:
        user.user_permissions.set(Permission.objects.all())

    user.user_permissions.add(Permission.objects.get(codename='privacy_level_1'))
    user.user_permissions.remove(Permission.objects.get(codename='privacy_level_2'))
    user.user_permissions.remove(Permission.objects.get(codename='access_study'))
    user.user_permissions.remove(Permission.objects.get(codename='search_participations'))

    return user


@pytest.fixture(scope='session', autouse=True)
def attribute_descriptions(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        create_attribute_descriptions.generate_attribute_descriptions()


@pytest.fixture(scope='session', autouse=True)
def groups(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        load_django_fixture('castellum_auth', 'groups')


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
def data_protection_coordinator(db):
    return create_user('Data protection coordinator')


@pytest.fixture
def receptionist(db):
    return create_user('Receptionist')


@pytest.fixture
def admin(db):
    user = create_user(None)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def study(db):
    return baker.make(Study)


@pytest.fixture
def study_in_execution_status(db):
    return baker.make(Study, status=Study.EXECUTION)


@pytest.fixture
def study_in_edit_status(db):
    return baker.make(Study, status=Study.EDIT)


@pytest.fixture
def member(study, study_in_execution_status, study_in_edit_status):
    user = create_user(None)
    StudyMembership.objects.create(user=user, study=study)
    StudyMembership.objects.create(user=user, study=study_in_execution_status)
    StudyMembership.objects.create(user=user, study=study_in_edit_status)
    return user


@pytest.fixture
def address(db):
    return baker.make(Address)


@pytest.fixture
def contact(db):
    return baker.make(Contact)


@pytest.fixture
def attributeset(contact):
    return baker.make(AttributeSet, subject=contact.subject)


@pytest.fixture
def participation(contact, study_in_execution_status):
    return baker.make(
        Participation, study=study_in_execution_status, subject=contact.subject
    )


@pytest.fixture
def attribute_description(db, attribute_descriptions):
    return AttributeDescription.objects.get(pk=1)


@pytest.fixture
def subject_filter_group(db, study_in_edit_status):
    return baker.make(SubjectFilterGroup, study=study_in_edit_status)


@pytest.fixture
def subject_filter(subject_filter_group, attribute_description):
    return SubjectFilter.objects.create(
        description=attribute_description,
        operator='exact',
        value='left',
        group=subject_filter_group,
    )
