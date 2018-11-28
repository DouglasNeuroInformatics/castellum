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

from .models import AttributeDescription
from .models import SubjectFilter


def get_description_choices():
    yield None, '---'
    for description in AttributeDescription.objects.all():
        yield description.pk, description.filter_label


class SubjectFilterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected_description = self._get_selected_description(**kwargs)

        if not selected_description:
            return

        filter_field = selected_description.get_filter_field()

        self.fields["description"].widget.attrs["disabled"] = True
        self.fields["description"].choices = get_description_choices()

        self.fields["operator"] = forms.ChoiceField(choices=filter_field.available_operators)

        self.fields["value"] = filter_field.formfield(selected_description)
        self.fields["value"].required = True

        # disable fields when study is not published
        try:
            if self.instance.group.study:
                if self.instance.group.study.published:
                    self.fields["operator"].widget.attrs["disabled"] = True
                    self.fields["value"].widget.attrs["disabled"] = True
        except ObjectDoesNotExist:
            pass

    def _get_selected_description(self, instance=None, data=None, prefix=None, **kwargs):
        if instance:
            return instance.description
        elif data:
            pk = data[prefix + '-description' if prefix else 'description']
            if pk:
                return AttributeDescription.objects.get(pk=pk)

    class Meta:
        model = SubjectFilter
        fields = "__all__"


class AttributeSetForm(forms.Form):
    def __init__(self, instance=None, **kwargs):
        self.instance = instance
        if not kwargs.get('initial'):
            kwargs['initial'] = instance.get_data()
        super().__init__(**kwargs)

    def save(self):
        self.instance.data.update(self.cleaned_data)
        self.instance.save()
        return self.instance

    @classmethod
    def factory(cls, user, obj=None):
        allowed_descriptions = AttributeDescription.objects.allowed(user, obj=obj)
        form_fields = {desc.name: desc.get_form_field() for desc in allowed_descriptions}
        return type('AttributeSetForm', (cls,), form_fields)
