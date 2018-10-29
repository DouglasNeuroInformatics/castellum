import pytest
from model_mommy import mommy

from django.contrib.auth.models import Permission

from castellum.recruitment.models import AttributeField
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study


@pytest.fixture
def study():
    return mommy.make(Study)


@pytest.fixture
def subject_filter_group(study):
    return mommy.make(SubjectFilterGroup, study=study)


@pytest.mark.django_db
def test_clone_with_empty_filter_group(subject_filter_group, study):
    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 0 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_clone_with_multiple_filters(subject_filter_group, attribute_field, study):
    SubjectFilter.objects.create(group=subject_filter_group, field=attribute_field,
                                 operator="operator1", value="value1")
    SubjectFilter.objects.create(group=subject_filter_group, field=attribute_field,
                                 operator="operator2", value="value2")

    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 2 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_attribute_field_creates_permissions():
    field = mommy.make(AttributeField, name='test')

    assert Permission.objects.filter(codename='view_attributeset_test').exists()
    assert Permission.objects.filter(codename='change_attributeset_test').exists()

    field.delete()

    assert not Permission.objects.filter(codename='view_attributeset_test').exists()
    assert not Permission.objects.filter(codename='change_attributeset_test').exists()
