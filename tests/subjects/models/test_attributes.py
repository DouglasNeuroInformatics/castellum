import pytest
from model_bakery import baker
from parler.utils.context import switch_language

from castellum.recruitment.models import AttributeCategory
from castellum.recruitment.models import AttributeChoice
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


@pytest.mark.django_db
def test_attribute_description_export():
    description = AttributeDescription.objects.create(
        field_type='ChoiceField',
        privacy_level_read=1,
        privacy_level_write=2,
        order=15,
    )
    with switch_language(description, 'en'):
        description.label = 'en-label'
        description._filter_label = 'en-filter-label'
        description.help_text = 'en-help-text'
    with switch_language(description, 'de'):
        description.label = 'de-label'
        description._filter_label = 'de-filter-label'
        description.help_text = 'de-help-text'
    description.save()

    choice1 = AttributeChoice.objects.create(description=description, order=2)
    with switch_language(choice1, 'en'):
        choice1.label = 'en-label1'
    with switch_language(choice1, 'de'):
        choice1.label = 'de-label1'
    choice1.save()

    choice2 = AttributeChoice.objects.create(description=description, order=1)
    with switch_language(choice2, 'en'):
        choice2.label = 'en-label2'
    with switch_language(choice2, 'de'):
        choice2.label = 'de-label2'
    choice2.save()

    assert description.export() == {
        'field_type': 'ChoiceField',
        'privacy_level_read': 1,
        'privacy_level_write': 2,
        'order': 15,
        'label': {
            'de': 'de-label',
            'en': 'en-label',
        },
        '_filter_label': {
            'de': 'de-filter-label',
            'en': 'en-filter-label',
        },
        'help_text': {
            'de': 'de-help-text',
            'en': 'en-help-text',
        },
        'choices': [{
            'label': {
                'de': 'de-label2',
                'en': 'en-label2',
            }
        }, {
            'label': {
                'de': 'de-label1',
                'en': 'en-label1',
            }
        }],
        'url': '',
    }
