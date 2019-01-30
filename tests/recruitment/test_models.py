import pytest
from model_mommy import mommy

from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeCategory
from castellum.recruitment.models.attributesets import UNCATEGORIZED
from castellum.studies.models import Study


@pytest.fixture
def study():
    return mommy.make(Study)


@pytest.fixture
def subject_filter_group(study):
    return mommy.make(SubjectFilterGroup, study=study)


@pytest.fixture
def attribute_category():
    return mommy.make(AttributeCategory)


@pytest.mark.django_db
def test_clone_with_empty_filter_group(subject_filter_group, study):
    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 0 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_clone_with_multiple_filters(subject_filter_group, attribute_description, study):
    SubjectFilter.objects.create(group=subject_filter_group, description=attribute_description,
                                 operator="operator1", value="value1")
    SubjectFilter.objects.create(group=subject_filter_group, description=attribute_description,
                                 operator="operator2", value="value2")

    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 2 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_attribute_description_by_category(attribute_descriptions):
    categories = AttributeDescription.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 3
    assert len(categories) == 1


@pytest.mark.django_db
def test_attribute_description_by_category_with_categories(
    attribute_descriptions, attribute_category
):
    description = AttributeDescription.objects.first()
    description.category = attribute_category
    description.save()

    categories = AttributeDescription.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 2
    assert len(categories) == 2


@pytest.mark.django_db
def test_attribute_description_by_category_with_qs(attribute_descriptions):
    qs = AttributeDescription.objects.filter(weight__lte=1)

    categories = AttributeDescription.objects.by_category(qs=qs)
    assert len(categories[UNCATEGORIZED]) == 2
    assert len(categories) == 1
