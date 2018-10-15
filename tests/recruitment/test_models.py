import pytest
from model_mommy import mommy

from castellum.recruitment.models import SubjectFilter, SubjectFilterGroup
from castellum.studies.models import Study


@pytest.fixture
def study():
    return mommy.make(Study)


@pytest.fixture
def subject_filter_group(study):
    return mommy.make(SubjectFilterGroup, study=study)


@pytest.mark.django_db
def test_duplicate_with_empty_filter_group(subject_filter_group, study):
    clone = subject_filter_group.duplicate()

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 0 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_duplicate_with_multiple_filters(subject_filter_group, study):
    SubjectFilter.objects.create(group=subject_filter_group, field_name="field1",
                                 operator="operator1", value="value1")
    SubjectFilter.objects.create(group=subject_filter_group, field_name="field2",
                                 operator="operator2", value="value2")

    clone = subject_filter_group.duplicate()

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 2 == clone.subjectfilter_set.count()
