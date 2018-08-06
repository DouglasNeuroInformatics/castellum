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


def get_field_name_choices():
    yield '', '---'
    for field in AttributeSet._meta.get_fields()[2:]:
        yield field.name, field.verbose_name


class SubjectFilterForm(forms.ModelForm):
    FILTER_MAPPING = {
        "CharField": TextFilter(),
        "DateField": DateFilter(),
        "FloatField": NumberFilter(),
        "IntegerField": NumberFilter(),
    }

    field_name = forms.ChoiceField(choices=get_field_name_choices())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected_field_name = self._get_selected_field_name(**kwargs)

        if not selected_field_name:
            return

        self.fields["field_name"].widget.attrs["disabled"] = True

        choices = self._get_operator_choices_by_field_name(selected_field_name)
        self.fields["operator"] = forms.ChoiceField(choices=choices)

        self.fields["value"] = self._get_value_field_by_field_name(selected_field_name)

    def _get_selected_field_name(self, instance=None, data=None, prefix=None, **kwargs):
        if instance:
            return instance.field_name
        elif data:
            if prefix:
                return data[prefix + '-field_name']
            else:
                return data['field_name']

    def _get_model_field_by_field_name(self, field_name):
        return AttributeSet._meta.get_field(field_name)

    def _get_operator_choices_by_field_name(self, field_name):
        model_field = self._get_model_field_by_field_name(field_name)
        subject_filter = self.FILTER_MAPPING[model_field.get_internal_type()]
        operators = subject_filter.available_operators
        return (tuple(operator) for operator in operators.items())

    def _get_value_field_by_field_name(self, field_name):
        model_field = self._get_model_field_by_field_name(field_name)
        return model_field.formfield()

    class Meta:
        model = SubjectFilter
        fields = "__all__"
