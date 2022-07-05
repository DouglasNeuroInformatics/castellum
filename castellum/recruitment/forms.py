# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

import json
from pathlib import Path

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from castellum.subjects.models import Subject
from castellum.utils.forms import BaseImportForm
from castellum.utils.forms import DisabledChoiceField
from castellum.utils.forms import DisabledModelChoiceField

from .models import AttributeDescription
from .models import Participation
from .models import SubjectFilter
from .models.attributes import ANSWER_DECLINED

APP_DIR = Path(__file__).resolve().parent
IMPORT_SCHEMA = json.load(open(APP_DIR / 'schemas' / 'attributes.json'))


def get_description_choices(user):
    choices = [(None, '---')]
    disabled_choices = []

    for description in AttributeDescription.objects.order_by('order'):
        choices.append((description.pk, description.filter_label))
        if not user.has_privacy_level(description.privacy_level_read):
            disabled_choices.append(description.pk)

    return choices, disabled_choices


class SubjectFilterAddForm(forms.Form):
    description = DisabledModelChoiceField(
        AttributeDescription.objects.none(), label=_('Attribute'), required=False
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices, disabled_choices = get_description_choices(user)
        self.fields["description"].choices = choices
        self.fields["description"].widget.disabled_choices = disabled_choices


class SubjectFilterForm(forms.ModelForm):
    class Meta:
        model = SubjectFilter
        fields = [
            'description',
            'operator',
            'value',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.desc = self._get_selected_description(**kwargs)

        self.fields["value"] = self.desc.field.filter_formfield(
            label=_('Filter value'), required=True
        )
        self.fields["operator"] = forms.ChoiceField(
            label=_('Comparison'), choices=self.desc.field.available_operators
        )

    def _get_selected_description(self, instance=None, data=None, prefix=None, **kwargs):
        if instance:
            return instance.description

        key = prefix + '-description' if prefix else 'description'
        if data and data[key]:
            try:
                return AttributeDescription.objects.get(pk=data[key])
            except AttributeDescription.DoesNotExist:
                return None

        try:
            return kwargs['initial']['description']
        except KeyError:
            return None


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


class AttributesForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['study_type_disinterest', 'anonymous_invitation_disinterest']
        widgets = {
            'study_type_disinterest': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, instance=None, **kwargs):
        if not kwargs.get('initial'):
            kwargs['initial'] = {}
            for key, value in instance.get_data().items():
                kwargs['initial'][key] = None if value == ANSWER_DECLINED else value
        super().__init__(instance=instance, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for key in cleaned_data:
            if key + '_answer_declined' in self.data:
                cleaned_data[key] = ANSWER_DECLINED
        study_type_disinterest = cleaned_data.pop('study_type_disinterest')
        anonymous_invitation_disinterest = cleaned_data.pop('anonymous_invitation_disinterest')
        return {
            'study_type_disinterest': study_type_disinterest,
            'anonymous_invitation_disinterest': anonymous_invitation_disinterest,
            'attributes': cleaned_data,
        }

    def save(self, *args, **kwargs):
        self.instance.attributes.update(self.cleaned_data['attributes'])
        return super().save(*args, **kwargs)

    @classmethod
    def factory(cls, user):
        allowed_descriptions = (
            AttributeDescription.objects
            .allowed_write(user)
            .exclude(id=settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID)
        )
        form_fields = {desc.json_key: desc.field.formfield() for desc in allowed_descriptions}
        return type('AttributesForm', (cls,), form_fields)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = [
            'status',
            'followup_date',
            'followup_time',
            'exclusion_criteria_checked',
            'assigned_recruiter',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        model_status = Participation._meta.get_field('status')
        self.fields['status'] = DisabledChoiceField(
            label=model_status.verbose_name,
            choices=model_status.choices,
            coerce=int,
        )
        if not self.instance.match:
            self.fields['status'].widget.disabled_choices = [
                choice for choice, label in Participation.STATUS_OPTIONS
                if choice != Participation.UNSUITABLE
            ]
        elif self.instance.match == 'incomplete':
            self.fields['status'].widget.disabled_choices = [Participation.INVITED]

        recruiter_pks = [recruiter.pk for recruiter in self.instance.study.recruiters]
        self.fields['assigned_recruiter'].queryset = self.instance.study.studymembership_set.filter(
            user_id__in=recruiter_pks
        )


class SendMailForm(forms.Form):
    batch_size = forms.IntegerField(
        min_value=1, label=_('How many subjects do you want to contact?')
    )


class DescriptionImportForm(BaseImportForm):
    schema = IMPORT_SCHEMA
    schema_ref = '#/$defs/AttributeDescriptionExport'
