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
        fields = AttributeSet._meta.get_fields()
        selected_field = list(filter(lambda f: f.name == selected_field_name, fields))[0]

        subject_filter = self.FILTER_MAPPING[selected_field.get_internal_type()]

        operators = subject_filter.available_operators
        choices = (tuple(operator) for operator in operators.items())
        self.fields["operator"].widget = forms.Select(choices=choices)

        values = AttributeSet.objects.values_list(selected_field_name, flat=True).distinct()
        choices = ((value, value) for value in values)
        self.fields["value"].widget = forms.Select(choices=choices)

    class Meta:
        model = SubjectFilter
        exclude = "study", "field_type"
