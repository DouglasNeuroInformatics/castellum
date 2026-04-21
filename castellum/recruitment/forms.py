# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from castellum.subjects.models import Subject
from castellum.utils.forms import DisabledChoiceField

from .models import Attribute
from .models import Participation
from .models import Relation
from .models import RelationType
from .models import SubjectFilter
from .models.attributes import ANSWER_DECLINED
from .models.attributes import UNCATEGORIZED


def get_attribute_choices():
    choices = [(None, '---')]

    categories = Attribute.objects.by_category()

    for attribute in categories.pop(UNCATEGORIZED):
        choices.append((attribute.pk, attribute.filter_label))

    for category, attributes in categories.items():
        sub = []
        for attribute in attributes:
            sub.append((attribute.pk, attribute.filter_label))
        choices.append((category.label, sub))

    return choices


class SubjectFilterAddForm(forms.Form):
    attribute = forms.ModelChoiceField(
        Attribute.objects.none(), label=_('Attribute'), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['attribute'].choices = get_attribute_choices()


class SubjectFilterForm(forms.ModelForm):
    class Meta:
        model = SubjectFilter
        fields = [
            'attribute',
            'operator',
            'value',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attr = self._get_selected_attribute(**kwargs)

        self.fields['value'] = self.attr.field.filter_formfield(
            label=_('Filter value'), required=True
        )
        self.fields['operator'] = forms.ChoiceField(
            label=_('Comparison'), choices=self.attr.field.available_operators
        )

    def _get_selected_attribute(self, instance=None, data=None, prefix=None, **kwargs):
        if instance:
            return instance.attribute

        key = f'{prefix}-attribute' if prefix else 'attribute'
        if data and data[key]:
            try:
                return Attribute.objects.get(pk=data[key])
            except Attribute.DoesNotExist:
                return None

        try:
            return kwargs['initial']['attribute']
        except KeyError:
            return None


class SubjectFilterFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()

        values = []
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                values.append((
                    form.cleaned_data.get('attribute'),
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
        fields = ['study_type_disinterest']
        widgets = {
            'study_type_disinterest': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, instance=None, **kwargs):
        if not kwargs.get('initial'):
            kwargs['initial'] = {}
            for attr in Attribute.objects.all():
                key = attr.json_key
                value = instance.attributes.get(key)
                kwargs['initial'][key] = None if value == ANSWER_DECLINED else value
        super().__init__(instance=instance, **kwargs)

    @staticmethod
    def get_date_of_birth_attribute_json_key():
        date_of_birth_attribute = Attribute.objects.filter(
            id=settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID
        ).first()
        if date_of_birth_attribute:
            return date_of_birth_attribute.json_key

        return None

    def clean(self):
        cleaned_data = super().clean()

        # Prevent date of birth being saved, it is meant to be read-only.
        cleaned_data.pop(self.get_date_of_birth_attribute_json_key(), None)

        for key in cleaned_data:
            if f'{key}_answer_declined' in self.data:
                cleaned_data[key] = ANSWER_DECLINED
        study_type_disinterest = cleaned_data.pop('study_type_disinterest')
        return {
            'study_type_disinterest': study_type_disinterest,
            'attributes': cleaned_data,
        }

    def save(self, *args, **kwargs):
        self.instance.attributes.update(self.cleaned_data['attributes'])
        return super().save(*args, **kwargs)

    @classmethod
    def factory(cls, subject):
        attributes = Attribute.objects.filter(
            privacy_level__lte=subject.get_effective_privacy_level()
        )
        form_fields = {attr.json_key: attr.field.formfield() for attr in attributes}

        # Date of birth attribute is read-only, it is changed through the "contact" tab
        date_of_birth_attribute_key = cls.get_date_of_birth_attribute_json_key()
        if date_of_birth_attribute_key:
            form_fields[date_of_birth_attribute_key].disabled = True

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
            choices=[(None, '---')] + [
                (choice, label) for choice, label in model_status.choices
                if choice in [
                    Participation.NOT_REACHED,
                    Participation.AWAITING_RESPONSE,
                    Participation.MAIL_SENT,
                    Participation.FOLLOWUP_APPOINTED,
                    Participation.PARTICIPATING,
                    Participation.EXCLUDED,
                ]
            ],
            coerce=int,
        )
        if not self.instance.is_match:
            self.fields['status'].widget.disabled_choices = [
                choice for choice, label in Participation.STATUS_OPTIONS
                if choice != Participation.EXCLUDED
            ]
        elif self.instance.is_match == 'incomplete':
            self.fields['status'].widget.disabled_choices = [
                Participation.PARTICIPATING
            ]

        recruiter_pks = [recruiter.pk for recruiter in self.instance.study.recruiters]
        self.fields['assigned_recruiter'].queryset = (
            self.instance.study.studymembership_set.filter(user_id__in=recruiter_pks)
        )


class RelationForm(forms.ModelForm):
    key = forms.ChoiceField(initial=None)

    class Meta:
        model = Relation
        fields = ['other']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['key'].label = Relation._meta.get_field('type').verbose_name
        keys = [(None, '----')]
        for t in RelationType.objects.all():
            keys.append((t.key, t.label))
            if t.reverse_key != t.key:
                keys.append((t.reverse_key, t.reverse_label))
        self.fields['key'].choices = keys


class SendMailForm(forms.Form):
    batch_size = forms.IntegerField(
        min_value=1, label=_('How many subjects do you want to contact?')
    )
