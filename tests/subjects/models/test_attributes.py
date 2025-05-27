import pytest
from model_bakery import baker

from castellum.recruitment.models import Attribute
from castellum.recruitment.models import AttributeCategory
from castellum.recruitment.models.attributes import UNCATEGORIZED


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
