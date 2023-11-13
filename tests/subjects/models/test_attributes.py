import pytest
from model_bakery import baker

from castellum.recruitment.models import Attribute
from castellum.recruitment.models import AttributeCategory
from castellum.recruitment.models.attributes import UNCATEGORIZED
from castellum.subjects.models import Subject


@pytest.mark.django_db
def test_attributes_get_completeness_empty():
    subject = Subject(attributes={})
    completed, total = subject.get_completeness()
    assert completed == 0


def test_attributes_get_completeness_empty_value(attribute):
    subject = Subject()
    subject.attributes = {
        attribute.json_key: None,
    }
    completed, total = subject.get_completeness()
    assert completed == 0


def test_attributes_get_completeness_non_empty(attribute):
    subject = Subject()
    subject.attributes = {
        attribute.json_key: 1,
    }
    completed, total = subject.get_completeness()
    assert completed == 1


@pytest.mark.django_db
def test_attribute_by_category(attributes):
    categories = Attribute.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 5
    assert len(categories) == 1


@pytest.mark.django_db
def test_attribute_by_category_with_categories(attributes):
    attribute = Attribute.objects.first()
    attribute.category = baker.make(AttributeCategory)
    attribute.save()

    categories = Attribute.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 4
    assert len(categories) == 2


@pytest.mark.django_db
def test_attribute_by_category_with_qs(attributes):
    qs = Attribute.objects.filter(order__lte=1)

    categories = Attribute.objects.by_category(qs=qs)
    assert len(categories[UNCATEGORIZED]) == 2
    assert len(categories) == 1
