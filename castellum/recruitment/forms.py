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
from django.core.exceptions import ObjectDoesNotExist

from .models import AttributeField
from .models import SubjectFilter


def get_field_name_choices():
    yield '', '---'
    for field in AttributeField.objects.all():
        yield field.name, field.filter_label


class SubjectFilterForm(forms.ModelForm):
    field_name = forms.ChoiceField(choices=get_field_name_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected_field_name = self._get_selected_field_name(**kwargs)

        if not selected_field_name:
            return

        attribute_field = AttributeField.objects.get(name=selected_field_name)
        filter_field = attribute_field.get_filter_field()

        self.fields["field_name"].widget.attrs["disabled"] = True

        self.fields["operator"] = forms.ChoiceField(choices=filter_field.available_operators)

        self.fields["value"] = filter_field.formfield(selected_field_name)
        self.fields["value"].required = True

        # disable fields when study is not published
        try:
            if self.instance.group.study:
                if self.instance.group.study.published:
                    self.fields["operator"].widget.attrs["disabled"] = True
                    self.fields["value"].widget.attrs["disabled"] = True
        except ObjectDoesNotExist:
            pass

    def _get_selected_field_name(self, instance=None, data=None, prefix=None, **kwargs):
        if instance:
            return instance.field_name
        elif data:
            if prefix:
                return data[prefix + '-field_name']
            else:
                return data['field_name']

    class Meta:
        model = SubjectFilter
        fields = "__all__"


class AttributeSetForm(forms.Form):
    def __init__(self, instance=None, **kwargs):
        self.instance = instance
        if not kwargs.get('initial'):
            kwargs['initial'] = instance.data
        super().__init__(**kwargs)

    def save(self):
        self.instance.data = self.cleaned_data
        self.instance.save()
        return self.instance

    @classmethod
    def factory(cls):
        fields = {field.name: field.get_form_field() for field in AttributeField.objects.all()}
        return type('AttributeSetForm', (cls,), fields)
