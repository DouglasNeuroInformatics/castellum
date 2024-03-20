import datetime

import pytest
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.db.models import DateField
from django.db.models import DateTimeField
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from castellum.castellum_auth.models import User
from castellum.contacts.models import Address
from castellum.contacts.models import Contact
from castellum.contacts.models import ContactCreationRequest
from castellum.recruitment.management.commands import create_demo_content
from castellum.recruitment.models import Attribute
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.studies.models import StudyGroup
from castellum.studies.models import StudyMembership
from castellum.subjects.models import SubjectCreationRequest

baker.generators.add(
    'castellum.utils.fields.DateField', baker.generators.default_mapping[DateField]
)
baker.generators.add(
    'castellum.utils.fields.DateTimeField',
    baker.generators.default_mapping[DateTimeField],
)
baker.generators.add(
    'castellum.utils.fields.PhoneNumberField',
    create_demo_content.fake_phone_number,
)

# monkey patch to make test isolation work on both databases
# See https://github.com/pytest-dev/pytest-django/pull/431
TestCase.databases = ['default', 'contacts']


def pytest_collection_modifyitems(items):
    # run migration tests last so they do not interfere with session scoped data
    items.sort(key=lambda item: 'migrator_factory' in getattr(item, 'fixturenames', []))


def create_user(group_name):
    future = timezone.now() + datetime.timedelta(days=10000)
    user = baker.make(User, expiration_date=future, email='test@example.com')

    if group_name == 'all':
        user.user_permissions.set(Permission.objects.all())
    elif group_name:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

    user.user_permissions.add(Permission.objects.get(codename='privacy_level_1'))
    user.user_permissions.remove(Permission.objects.get(codename='privacy_level_2'))
    user.user_permissions.remove(Permission.objects.get(codename='access_study'))
    user.user_permissions.remove(
        Permission.objects.get(codename='search_participations')
    )

    return user


def create_member(group_name, studies):
    if group_name == 'all':
        user = create_user('all')
    else:
        user = create_user(None)

    for study in studies:
        membership = StudyMembership.objects.create(user=user, study=study)
        if group_name and group_name != 'all':
            group = StudyGroup.objects.get(name=group_name)
            membership.groups.add(group)

    return user


@pytest.fixture(scope='session', autouse=True)
def attributes(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'attributes')
        call_command('loaddata', 'attributes_extra')


@pytest.fixture(scope='session', autouse=True)
def groups(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'groups')


@pytest.fixture(scope='session', autouse=True)
def study_types(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'study_types')


@pytest.fixture(scope='session', autouse=True)
def study_groups(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'study_groups')


@pytest.fixture
def user(db):
    return create_user('all')


@pytest.fixture
def study_approver(db):
    return create_user('Study approver')


@pytest.fixture
def study_coordinator(db):
    return create_user('Study coordinator')


@pytest.fixture
def subject_manager(db):
    return create_user('Subject manager')


@pytest.fixture
def data_protection_coordinator(db):
    return create_user('Data protection coordinator')


@pytest.fixture
def receptionist(db):
    return create_user('Receptionist')


@pytest.fixture
def member(study, draft_study):
    return create_member('all', [study, draft_study])


@pytest.fixture
def recruiter(study, draft_study):
    return create_member('Recruiter', [study, draft_study])


@pytest.fixture
def conductor(study, draft_study):
    return create_member('Conductor', [study, draft_study])


@pytest.fixture
def admin(db):
    user = create_user('all')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def study(db):
    return baker.make(Study, status=Study.EXECUTION)


@pytest.fixture
def draft_study(db):
    return baker.make(Study, status=Study.EDIT)


@pytest.fixture
def address(db):
    return baker.make(Address)


@pytest.fixture
def contact(db):
    return baker.make(Contact)


@pytest.fixture
def subject(contact):
    return contact.subject


@pytest.fixture
def subject_creation_request(db):
    subject_creation_request = baker.make(SubjectCreationRequest)
    baker.make(ContactCreationRequest, subject_id=subject_creation_request.pk)
    return subject_creation_request


@pytest.fixture
def participation(subject, study):
    return baker.make(Participation, study=study, subject=subject)


@pytest.fixture
def invited(subject, study):
    return baker.make(
        Participation,
        study=study,
        subject=subject,
        status=Participation.PARTICIPATING,
    )


@pytest.fixture
def attribute(db, attributes):
    return Attribute.objects.get(pk=1)


@pytest.fixture
def subject_filter_group(db, study):
    return baker.make(SubjectFilterGroup, study=study)


@pytest.fixture
def subject_filter(subject_filter_group, attribute):
    return SubjectFilter.objects.create(
        attribute=attribute,
        operator='exact',
        value=1,
        group=subject_filter_group,
    )
