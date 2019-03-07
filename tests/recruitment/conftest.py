import pytest
from model_mommy import mommy

from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.management.commands import populate
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup


@pytest.fixture
def attributeset(contact):
    subject = get_subject(contact.pseudonym)
    return mommy.make(AttributeSet, subject=subject)


@pytest.fixture
def participation_request(contact, study):
    subject = get_subject(contact.pseudonym)
    return mommy.make(ParticipationRequest, study=study, subject=subject)


@pytest.fixture(scope='session')
def attribute_descriptions(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        populate.generate_attribute_descriptions()


@pytest.fixture
def attribute_description(db, attribute_descriptions):
    return AttributeDescription.objects.get(pk=1)


@pytest.fixture
def subject_filter_group(db, unpublished_study):
    return mommy.make(SubjectFilterGroup, study=unpublished_study)


@pytest.fixture
def subject_filter(subject_filter_group, attribute_description):
    return SubjectFilter.objects.create(
        description=attribute_description,
        operator='exact',
        value='left',
        group=subject_filter_group)
