# (c) 2018
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

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
        selected_field = AttributeSet._meta.get_field(selected_field_name)
        return self.FILTER_MAPPING[selected_field.get_internal_type()]

    def _get_operator_choices_from_subject_filter(self, subject_filter):
        operators = subject_filter.available_operators
        return (tuple(operator) for operator in operators.items())

    def _get_value_choices_for_selected_field_name(self, selected_field_name):
        values = AttributeSet.objects.values_list(selected_field_name, flat=True).distinct()
        return ((value, value) for value in values)

    class Meta:
        model = SubjectFilter
        exclude = "study", "field_type"
