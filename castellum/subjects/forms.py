# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django import forms
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from castellum.utils.forms import DatalistWidget

from .models import Consent
from .models import ConsentDocument
from .models import Subject


class DataProtectionForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['privacy_level']
        widgets = {
            'privacy_level': forms.RadioSelect(choices=sorted([
                (0.0, _('0 (regular)')),
                (1.0, _('1 (increased)')),
                (2.0, _('2 (high)')),
                *settings.CASTELLUM_CUSTOM_PRIVACY_LEVELS,
            ])),
        }

    to_be_deleted = forms.BooleanField(
        label=_('To be deleted'),
        required=False,
        help_text=Subject._meta.get_field('to_be_deleted').help_text,
    )
    export_requested = forms.BooleanField(
        label=_('Export requested'),
        required=False,
        help_text=Subject._meta.get_field('export_requested').help_text,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.fields['to_be_deleted'].initial = self.instance.to_be_deleted
        self.fields['export_requested'].initial = self.instance.export_requested

    def clean(self):
        cleaned_data = super().clean()

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(
                _('Please choose lower privacy level for the subject.'), code='invalid'
            )

        if (
            cleaned_data.get('to_be_deleted')
            and self.instance.has_consent_with_ineffective
        ):
            raise ValidationError(
                _(
                    'Subjects can either be marked for deletion or have '
                    'recruitment consent, not both.'
                ),
                code='invalid',
            )

        return cleaned_data

    def save(self, *args, **kwargs):
        if not self.cleaned_data.get('to_be_deleted'):
            self.instance.to_be_deleted = None
        elif not self.instance.to_be_deleted:
            self.instance.to_be_deleted = datetime.date.today()

        if not self.cleaned_data.get('export_requested'):
            self.instance.export_requested = None
        elif not self.instance.export_requested:
            self.instance.export_requested = datetime.date.today()

        subject = super().save(*args, **kwargs)

        return subject


class SubjectPrivacyLevelForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['privacy_level']
        widgets = {
            'privacy_level': forms.RadioSelect(choices=sorted([
                (0.0, _('0 (regular)')),
                (1.0, _('1 (increased)')),
                (2.0, _('2 (high)')),
                *settings.CASTELLUM_CUSTOM_PRIVACY_LEVELS,
            ])),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(
                _('Please choose lower privacy level for the subject.'),
                code='invalid',
            )
        return cleaned_data


class SubjectDeleteForm(forms.Form):
    create_block_hash = forms.BooleanField(
        label=_('Block this subject from future recruitment'),
        required=False,
        help_text=_(
            'A hash of the name will be retained so that contacting '
            'this subject again can be avoided even after all contact '
            'data has been deleted.'
        ),
    )


class SubjectMergeForm(forms.Form):
    target = forms.UUIDField(label=_('Target UUID'), required=True)


class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            'deceased',
            'not_available_until',
            'source',
        ]
        widgets = {
            'source': DatalistWidget(datalist=(
                Subject.objects
                .order_by('source')
                .values_list('source', flat=True)
                .distinct
            )),
        }


class ConsentChangeForm(forms.ModelForm):
    class Meta:
        model = Consent
        fields = ['document', 'file', 'excluded_by_us']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not ConsentDocument.objects.filter(is_valid=True).exists():
            ConsentDocument.objects.create()

        self.fields['document'].queryset = ConsentDocument.objects.filter(is_valid=True)
        self.fields['document'].empty_label = None
        self.fields['document'].empty_values = ['excluded', 'withdrawn']
        self.fields['document'].choices = [
            ('excluded', _(
                'Excluded by us (e.g. because they were unreliable or inactive)'
            )),
            ('withdrawn', _('Consent declined/withdrawn')),
            *self.fields['document'].choices,
        ]

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['excluded_by_us'] = self.data.get('document') == 'excluded'
        return cleaned_data
