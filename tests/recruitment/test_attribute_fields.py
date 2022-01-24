import datetime
import math

from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment import attribute_fields
from castellum.recruitment.models import AttributeChoice
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import SubjectFilter
from castellum.subjects.models import Subject


def test_number_display(attribute_description):
    field = attribute_fields.NumberAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display(15) == 15


def test_number_filter_display(attribute_description):
    field = attribute_fields.NumberAttributeField(attribute_description)
    assert field.get_filter_display('exact', 15) == 'Handedness == 15'


def test_boolean_display(attribute_description):
    field = attribute_fields.BooleanAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display(True) is True


def test_boolean_filter_display(attribute_description):
    field = attribute_fields.BooleanAttributeField(attribute_description)
    assert field.get_filter_display('exact', True) == 'Handedness is True'


def test_text_display(attribute_description):
    field = attribute_fields.TextAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display('asd') == 'asd'


def test_text_filter_display(attribute_description):
    field = attribute_fields.TextAttributeField(attribute_description)
    assert field.get_filter_display('exact', 'asd') == 'Handedness is asd'


def test_choice_display(attribute_description):
    field = attribute_fields.ChoiceAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display('') == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display(1) == 'Right'


def test_choice_filter_display(attribute_description):
    field = attribute_fields.ChoiceAttributeField(attribute_description)
    assert field.get_filter_display('exact', 1) == 'Handedness is Right'


def test_multiple_choice_display(attribute_description):
    field = attribute_fields.MultipleChoiceAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display([]) == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display(1) == 'Right'
    assert field.get_display([2, 1]) == 'Left, Right'


def test_multiple_choice_filter_display(attribute_description):
    field = attribute_fields.MultipleChoiceAttributeField(attribute_description)
    assert field.get_filter_display('contains', [2, 1]) == 'Handedness contains Left, Right'


def test_multiple_choice_filter(db):
    description = baker.make(AttributeDescription, field_type='MultipleChoiceField')
    choice1 = baker.make(AttributeChoice, description=description)
    choice2 = baker.make(AttributeChoice, description=description)

    baker.make(Subject, attributes={description.json_key: []})
    baker.make(Subject, attributes={description.json_key: [choice1.pk]})
    baker.make(Subject, attributes={description.json_key: [choice1.pk, choice2.pk]})

    count = Subject.objects.filter(description.field.filter_to_q('contains', choice1.pk)).count()
    assert count == 2


def test_age_display(attribute_description):
    field = attribute_fields.AgeAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display('1970-01-01') == datetime.date(1970, 1, 1)


def test_age_filter_display(attribute_description):
    field = attribute_fields.AgeAttributeField(attribute_description)
    assert field.get_filter_display('gt', (5, 'years')) == 'Handedness younger than 5 years'


def test_age_statistics_bucket(attribute_description, study):
    field = attribute_fields.AgeAttributeField(attribute_description)
    with freeze_time('1970-01-01'):
        buckets, get_bucket = field.get_statistics_grouping(study)
        assert get_bucket('1971-01-01') == 17
        assert get_bucket('1970-01-01') == 17
        assert get_bucket('1969-01-01') == 17
        assert get_bucket('1951-01-01') == 25
        assert get_bucket('1899-01-01') == math.inf


def test_age_statistics_bucket_children(attribute_description, study):
    baker.make(
        SubjectFilter,
        group__study=study,
        description=attribute_description,
        value=(24, 'months'),
        operator='gt',
    )

    field = attribute_fields.AgeAttributeField(attribute_description)
    with freeze_time('1970-01-01'):
        buckets, get_bucket = field.get_statistics_grouping(study)
        assert get_bucket('1969-01-01') == 12
        assert get_bucket('1969-01-02') == 11
        assert get_bucket('1970-01-01') == 0
        assert get_bucket('1969-10-01') == 3
        assert get_bucket('1900-01-01') is None
