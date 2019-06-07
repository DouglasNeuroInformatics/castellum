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
from django.utils.translation import ugettext_lazy as _

from castellum.utils.forms import DisabledChoiceField
from castellum.utils.forms import DisabledModelChoiceField
from castellum.utils.helpers import get_object_or_none

from .models import AttributeDescription
from .models import ParticipationRequest
from .models import SubjectFilter
from .models.attributesets import ANSWER_DECLINED
from .models.attributesets import UNCATEGORIZED


def get_description_choices(user):
    choices = [(None, '---')]
    disabled_choices = []

    categories = AttributeDescription.objects.by_category()

    for description in categories.pop(UNCATEGORIZED):
        choices.append((description.pk, description.filter_label))
        if not user.has_privacy_level(description.privacy_level_read):
            disabled_choices.append(description.pk)

    for category, descriptions in categories.items():
        sub = []
        for description in descriptions:
            sub.append((description.pk, description.filter_label))
            if not user.has_privacy_level(description.privacy_level_read):
                disabled_choices.append(description.pk)
        choices.append((category.label, sub))

    return choices, disabled_choices


class SubjectFilterForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected_description = self._get_selected_description(**kwargs)

        choices, disabled_choices = get_description_choices(user)
        self.fields["description"] = DisabledModelChoiceField(AttributeDescription.objects.all())
        self.fields["description"].choices = choices
        self.fields["description"].widget.disabled_choices = disabled_choices

        if not selected_description:
            return

        self.fields["description"].widget.attrs["disabled"] = True

        self.fields["operator"] = forms.ChoiceField(
            choices=selected_description.field.available_operators)

        self.fields["value"] = selected_description.field.filter_formfield()
        self.fields["value"].required = True

        # disable fields when study is not published
        try:
            if self.instance.group.study:
                if self.instance.group.study.recruitment_mode:
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
                return get_object_or_none(AttributeDescription, pk=pk)
        elif kwargs.get('initial') and kwargs['initial'].get('description'):
            return kwargs['initial']['description']

    class Meta:
        model = SubjectFilter
        fields = "__all__"


class SubjectFilterFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()

        values = []
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                values.append((
                    form.cleaned_data.get('description'),
                    form.cleaned_data.get('operator'),
                    form.cleaned_data.get('value'),
                ))

        if len(set(values)) != len(values):
            raise forms.ValidationError(_(
                'There are duplicates in filters. Please change or delete filters!'
            ), code='invalid')


class AttributeSetForm(forms.Form):
    def __init__(self, instance=None, **kwargs):
        self.instance = instance
        if not kwargs.get('initial'):
            kwargs['initial'] = {}
            for key, value in instance.get_data().items():
                kwargs['initial'][key] = None if value == ANSWER_DECLINED else value
        super().__init__(**kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for key in cleaned_data:
            if key + '_answer_declined' in self.data:
                cleaned_data[key] = ANSWER_DECLINED
        return cleaned_data

    def save(self):
        self.instance.data.update(self.cleaned_data)
        self.instance.save()
        return self.instance

    @classmethod
    def factory(cls, user, obj=None):
        allowed_descriptions = AttributeDescription.objects.allowed_write(user, obj=obj)
        form_fields = {desc.json_key: desc.field.formfield() for desc in allowed_descriptions}
        return type('AttributeSetForm', (cls,), form_fields)


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        model_status = ParticipationRequest._meta.get_field('status')
        self.fields['status'] = DisabledChoiceField(
            label=model_status.verbose_name,
            choices=model_status.choices,
            coerce=int,
        )
        if not self.instance.match:
            self.fields['status'].widget.disabled_choices = [
                choice for choice, label in ParticipationRequest.STATUS_OPTIONS
                if choice != ParticipationRequest.UNSUITABLE
            ]
        elif self.instance.match == 'incomplete':
            self.fields['status'].widget.disabled_choices = [ParticipationRequest.INVITED]

    class Meta:
        model = ParticipationRequest
        fields = ['status', 'appointment', 'exclusion_criteria_checked']
