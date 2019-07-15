import os

from django.conf import settings
from django.core import serializers
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.db.models import DateField
from django.utils import timezone

import pytest
from model_mommy import mommy

from castellum.castellum_auth.models import User
from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership

mommy.generators.add(
    'castellum.utils.fields.DateField', mommy.generators.default_mapping[DateField])


def load_django_fixture(app_label, name):
    path = os.path.join('castellum', app_label, 'fixtures', name + '.json')
    with open(path) as fh:
        for obj in serializers.deserialize('json', fh):
            obj.save()


def create_user(group_name):
    future = timezone.now() + timezone.timedelta(days=10000)
    user = User.objects.create(expiration_date=future)

    if group_name:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
    else:
        user.user_permissions.set(Permission.objects.all())

    user.user_permissions.add(Permission.objects.get(codename='privacy_level_1'))
    user.user_permissions.remove(Permission.objects.get(codename='privacy_level_2'))

    return user


@pytest.fixture
def sample_groups(db):
    load_django_fixture('castellum_auth', 'sample_groups')


@pytest.fixture
def user(db):
    return create_user(None)


@pytest.fixture
def study_coordinator(sample_groups):
    return create_user('Study coordinator')


@pytest.fixture
def subject_manager(sample_groups):
    return create_user('Subject manager')


@pytest.fixture
def recruiter(sample_groups):
    return create_user('Recruiter')


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
def study_in_recruitment_mode(db):
    return mommy.make(Study, study_mode=Study.RECRUITMENT)


@pytest.fixture
def study_in_edit_mode(db):
    return mommy.make(Study, study_mode=Study.EDIT)


@pytest.fixture
def member(user, study, study_in_recruitment_mode, study_in_edit_mode):
    StudyMembership.objects.create(user=user, study=study)
    StudyMembership.objects.create(user=user, study=study_in_recruitment_mode)
    StudyMembership.objects.create(user=user, study=study_in_edit_mode)
    return user


@pytest.fixture
def contact(db):
    return mommy.make(Contact, pseudonym=None)


@pytest.fixture
def attributeset(contact):
    subject = get_subject(settings.DOMAINS['contact'], contact.pseudonym)
    return mommy.make(AttributeSet, subject=subject)


@pytest.fixture
def participation_request(contact, study_in_recruitment_mode):
    subject = get_subject(settings.DOMAINS['contact'], contact.pseudonym)
    return mommy.make(ParticipationRequest, study=study_in_recruitment_mode, subject=subject)


@pytest.fixture
def attribute_descriptions(db):
    load_django_fixture('recruitment', 'attribute_descriptions')


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
