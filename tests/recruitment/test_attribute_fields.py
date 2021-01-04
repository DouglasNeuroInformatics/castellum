import datetime

from freezegun import freeze_time

from castellum.recruitment import attribute_fields


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
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display(1) == 'Right'


def test_choice_filter_display(attribute_description):
    field = attribute_fields.ChoiceAttributeField(attribute_description)
    assert field.get_filter_display('exact', 1) == 'Handedness is Right'


def test_multiple_choice_display(attribute_description):
    field = attribute_fields.MultipleChoiceAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display(1) == 'Right'
    assert field.get_display([2, 1]) == 'Left, Right'


def test_multiple_choice_filter_display(attribute_description):
    field = attribute_fields.MultipleChoiceAttributeField(attribute_description)
    assert field.get_filter_display('contains', [2, 1]) == 'Handedness contains Left, Right'


def test_age_display(attribute_description):
    field = attribute_fields.AgeAttributeField(attribute_description)
    assert field.get_display(None) == '—'
    assert field.get_display(attribute_fields.ANSWER_DECLINED) == 'Declined to answer'
    assert field.get_display('1970-01-01') == datetime.date(1970, 1, 1)


def test_age_filter_display(attribute_description):
    field = attribute_fields.AgeAttributeField(attribute_description)
    assert field.get_filter_display('gt', (5, 'years')) == 'Handedness younger than 5 years'


def test_age_statistics_bucket(attribute_description):
    field = attribute_fields.AgeAttributeField(attribute_description)
    with freeze_time('1970-01-01'):
        buckets, get_bucket = field.get_statistics_grouping()
        assert get_bucket('1971-01-01') == '<18'
        assert get_bucket('1970-01-01') == '<18'
        assert get_bucket('1969-01-01') == '<18'
        assert get_bucket('1951-01-01') == '18-25'
        assert get_bucket('1899-01-01') == '>70'
