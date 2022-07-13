import pytest
from model_bakery import baker

from castellum.recruitment.models import AttributeCategory
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models.attributes import UNCATEGORIZED
from castellum.subjects.models import Subject


@pytest.mark.django_db
def test_attributes_get_completeness_empty():
    subject = Subject(attributes={})
    completed, total = subject.get_completeness()
    assert completed == 0


def test_attributes_get_completeness_empty_value(attribute_description):
    subject = Subject()
    subject.attributes = {
        attribute_description.json_key: None,
    }
    completed, total = subject.get_completeness()
    assert completed == 0


def test_attributes_get_completeness_non_empty(attribute_description):
    subject = Subject()
    subject.attributes = {
        attribute_description.json_key: 1,
    }
    completed, total = subject.get_completeness()
    assert completed == 1


@pytest.mark.django_db
def test_attribute_description_by_category(attribute_descriptions):
    categories = AttributeDescription.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 5
    assert len(categories) == 1


@pytest.mark.django_db
def test_attribute_description_by_category_with_categories(attribute_descriptions):
    description = AttributeDescription.objects.first()
    description.category = baker.make(AttributeCategory)
    description.save()

    categories = AttributeDescription.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 4
    assert len(categories) == 2


@pytest.mark.django_db
def test_attribute_description_by_category_with_qs(attribute_descriptions):
    qs = AttributeDescription.objects.filter(order__lte=1)

    categories = AttributeDescription.objects.by_category(qs=qs)
    assert len(categories[UNCATEGORIZED]) == 2
    assert len(categories) == 1
