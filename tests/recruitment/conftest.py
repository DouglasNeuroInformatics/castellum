from django.conf import settings

import pytest
from model_mommy import mommy

from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import SubjectFilterGroup


@pytest.fixture
def attributeset(contact):
    pseudonym = resolve_pseudonym(
        settings.DOMAINS['contact'], contact.pseudonym, AttributeSet.domain)
    return mommy.make(AttributeSet, pseudonym=pseudonym)


@pytest.fixture
def participation_request(contact, study):
    pseudonym = resolve_pseudonym(
        settings.DOMAINS['contact'], contact.pseudonym, study.domain)
    return mommy.make(ParticipationRequest, study=study, pseudonym=pseudonym)


@pytest.fixture
def filter_group(unpublished_study):
    return mommy.make(SubjectFilterGroup, study=unpublished_study)
