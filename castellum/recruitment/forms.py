from django import forms

from castellum.recruitment.models import AttributeSet

from .models import DateFilter
from .models import NumberFilter
from .models import SubjectFilter
from .models import TextFilter


class SelectAttributeForm(forms.Form):
    CHOICES = ((field.name, field.name) for field in AttributeSet._meta.get_fields()[2:])

    field_name = forms.ChoiceField(choices=CHOICES)


class AddSubjectFilterForm(forms.ModelForm):
    FILTER_MAPPING = {
        "CharField": TextFilter(),
        "DateField": DateFilter(),
        "FloatField": NumberFilter(),
        "IntegerField": NumberFilter(),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["field_name"].widget.attrs["readonly"] = True

        if "initial" not in kwargs:
            return
        if "field_name" not in kwargs["initial"]:
            return

        selected_field_name = kwargs["initial"]["field_name"]
        subject_filter = self._get_subject_filter_for_selected_field_name(selected_field_name)

        choices = self._get_operator_choices_from_subject_filter(subject_filter)
        self.fields["operator"].widget = forms.Select(choices=choices)

        choices = self._get_value_choices_for_selected_field_name(selected_field_name)
        self.fields["value"].widget = forms.Select(choices=choices)

    def _get_subject_filter_for_selected_field_name(self, selected_field_name):
        selected_field = self._get_selected_field_from_attribute_set(selected_field_name)
        return self.FILTER_MAPPING[selected_field.get_internal_type()]

    def _get_selected_field_from_attribute_set(self, selected_field_name):
        fields = AttributeSet._meta.get_fields()
        return list(filter(lambda f: f.name == selected_field_name, fields))[0]

    def _get_operator_choices_from_subject_filter(self, subject_filter):
        operators = subject_filter.available_operators
        return (tuple(operator) for operator in operators.items())

    def _get_value_choices_for_selected_field_name(self, selected_field_name):
        values = AttributeSet.objects.values_list(selected_field_name, flat=True).distinct()
        return ((value, value) for value in values)

    class Meta:
        model = SubjectFilter
        exclude = "study", "field_type"
