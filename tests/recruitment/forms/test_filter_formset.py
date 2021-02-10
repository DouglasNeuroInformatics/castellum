from django.forms import modelformset_factory

from castellum.recruitment.forms import SubjectFilterFormSet
from castellum.recruitment.models import SubjectFilter


def instantiate_formset(formset_class, data, instance=None, initial=None):
    prefix = formset_class().prefix
    formset_data = {}
    for i, form_data in enumerate(data):
        for name, value in form_data.items():
            if isinstance(value, list):
                for j, inner in enumerate(value):
                    formset_data[f'{prefix}-{i}-{name}_{j}'] = inner
            else:
                formset_data[f'{prefix}-{i}-{name}'] = value
    formset_data[f'{prefix}-TOTAL_FORMS'] = len(data)
    formset_data[f'{prefix}-INITIAL_FORMS'] = 0

    if instance:
        return formset_class(formset_data, instance=instance, initial=initial)
    else:
        return formset_class(formset_data, initial=initial)


def test_formset_with_arbitary_data(attribute_description):
    filterFormSet = modelformset_factory(
        SubjectFilter,
        fields=['description', 'operator', 'value'],
        formset=SubjectFilterFormSet,
        extra=0,
        max_num=5,
        min_num=1,
        can_delete=True,
    )

    formset = instantiate_formset(filterFormSet, [
        {'foo': 'bar1'},
        {'foo': 'bar2'},
    ])

    assert formset.is_valid() is False


def test_formset_with_valid_data(attribute_description):
    filterFormSet = modelformset_factory(
        SubjectFilter,
        fields=['description', 'operator', 'value'],
        formset=SubjectFilterFormSet,
        extra=0,
        max_num=5,
        min_num=1,
        can_delete=True,
    )

    formset = instantiate_formset(filterFormSet, [
        {
            'description': attribute_description.pk,
            'operator': 'contains',
            'value': 2,
            'DELETE': 'False',
        },
        {
            'description': attribute_description.pk,
            'operator': 'contains',
            'value': 1,
            'DELETE': 'False',
        },
    ])

    assert formset.is_valid() is True


def test_two_identical_filters(attribute_description):
    filterFormSet = modelformset_factory(
        SubjectFilter,
        fields=['description', 'operator', 'value'],
        formset=SubjectFilterFormSet,
        extra=0,
        max_num=5,
        min_num=1,
        can_delete=True,
    )

    formset = instantiate_formset(filterFormSet, [
        {
            'description': attribute_description.pk,
            'operator': 'contains',
            'value': 2,
            'DELETE': False,
        },
        {
            'description': attribute_description.pk,
            'operator': 'contains',
            'value': 2,
            'DELETE': False,
        },
    ])

    assert formset.is_valid() is False


def test_two_identical_filters_with_delete(attribute_description):
    filterFormSet = modelformset_factory(
        SubjectFilter,
        fields=['description', 'operator', 'value'],
        formset=SubjectFilterFormSet,
        extra=0,
        max_num=5,
        min_num=1,
        can_delete=True,
    )

    formset = instantiate_formset(filterFormSet, [
        {
            'description': attribute_description.pk,
            'operator': 'contains',
            'value': 2,
            'DELETE': False,
        },
        {
            'description': attribute_description.pk,
            'operator': 'contains',
            'value': 2,
            'DELETE': True,
        },
    ])

    assert formset.is_valid() is True
