import pytest
from model_mommy import mommy

from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup


@pytest.fixture
def subject_filter_group(db, unpublished_study):
    return mommy.make(SubjectFilterGroup, study=unpublished_study)


@pytest.fixture
def subject_filter(subject_filter_group):
    return SubjectFilter.objects.create(
        field_name='handedness',
        operator='exact',
        value='left',
        group=subject_filter_group)
