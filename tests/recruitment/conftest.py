import pytest
from model_mommy import mommy

from castellum.studies.models import Study
from castellum.subject_management.models import Subject


@pytest.fixture
def study(db):
    return mommy.make(Study)


@pytest.fixture
def subject(db):
    return mommy.make(Subject, pseudonym=None)
