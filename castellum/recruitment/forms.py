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
    CHOICES = ((field.name, field.verbose_name) for field in AttributeSet._meta.get_fields()[2:])

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

        choices = self._get_operator_choices_by_field_name(selected_field_name)
        self.fields["operator"] = forms.ChoiceField(choices=choices)

        choices = self._get_value_choices_by_field_name(selected_field_name)
        self.fields["value"] = forms.ChoiceField(choices=choices)

    def _get_model_field_by_field_name(self, field_name):
        return AttributeSet._meta.get_field(field_name)

    def _get_operator_choices_by_field_name(self, field_name):
        model_field = self._get_model_field_by_field_name(field_name)
        subject_filter = self.FILTER_MAPPING[model_field.get_internal_type()]
        operators = subject_filter.available_operators
        return (tuple(operator) for operator in operators.items())

    def _get_value_choices_by_field_name(self, field_name):
        values = AttributeSet.objects.values_list(field_name, flat=True).distinct()
        return ((value, value) for value in values)

    class Meta:
        model = SubjectFilter
        exclude = "study",
