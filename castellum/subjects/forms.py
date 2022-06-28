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

import datetime

from django import forms
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from castellum.utils.forms import DatalistWidget

from .models import Consent
from .models import ConsentDocument
from .models import Subject


def get_initial_consent_status(subject):
    if subject.has_consent:
        if ConsentDocument.objects.filter(consent__subject=subject).exists():
            return ConsentDocument.objects.filter(consent__subject=subject).first()
        else:
            return Subject.CONSENT_DECLINED
    else:
        return Subject.NO_CONSENT


def get_consent_choices(subject):
    if not ConsentDocument.objects.exists():
        ConsentDocument.objects.create()

    consent_documents = [(document.pk, document) for document in ConsentDocument.objects.all()]
    if subject.has_consent:
        choices = [Subject.CONSENT_DECLINED] + consent_documents
        return choices
    else:
        choices = [Subject.CONSENT_DECLINED] + [Subject.NO_CONSENT] + consent_documents
        return choices


class DataProtectionForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['privacy_level']
        widgets = {
            'privacy_level': forms.RadioSelect(choices=sorted([
                (0.0, _('0 (regular)')),
                (1.0, _('1 (increased)')),
                (2.0, _('2 (high)')),
            ] + settings.CASTELLUM_CUSTOM_PRIVACY_LEVELS)),
        }

    consent_status = forms.ChoiceField(
        label=_("Consent"),
        required=False
    )

    to_be_deleted = forms.BooleanField(
        label=_("To be deleted"),
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
        self.fields['consent_status'].initial = get_initial_consent_status(self.instance)

        self.fields['consent_status'].choices = get_consent_choices(self.instance)

    def clean(self):
        cleaned_data = super().clean()

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(
                _("Please choose lower privacy level for the subject."), code='invalid'
            )

        if cleaned_data.get('to_be_deleted') and cleaned_data.get('consent_status'):
            raise ValidationError(
                _(
                    'Subjects can either be marked for deletion or have recruitment consent, '
                    'not both.'
                ),
                code='invalid',
            )

        return cleaned_data

    def save_consent(self, subject):
        new_status = self.cleaned_data.get('consent_status')
        initial_status = get_initial_consent_status(subject)
        if initial_status == new_status or new_status == '':
            return
        elif new_status == Subject.CONSENT_DECLINED:
            subject.consent.delete()
            Consent.objects.create(
                subject=subject,
            )
        else:
            if Consent.objects.filter(subject=subject).exists():
                subject.consent.delete()
            document = ConsentDocument.objects.filter(pk=new_status).first()
            Consent.objects.create(
                subject=subject,
                underage_when_given=subject.contact.is_underage,
                document=document
            )

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
        self.save_consent(subject)

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
            ] + settings.CASTELLUM_CUSTOM_PRIVACY_LEVELS)),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(
                _("Please choose lower privacy level for the subject."),
                code='invalid',
            )
        return cleaned_data


class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            'deceased',
            'blocked',
            'not_available_until',
            'source',
            'additional_suitability_document',
        ]
        widgets = {
            'additional_suitability_document': forms.CheckboxSelectMultiple(),
            'source': DatalistWidget(datalist=(
                Subject.objects.order_by('source').values_list('source', flat=True).distinct
            )),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rm_subject_notes'] = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=self.instance.subjectnote_set.all(),
            required=False,
        )

    def save(self, *args, **kwargs):
        subject = super().save(*args, **kwargs)
        for note in self.cleaned_data['rm_subject_notes']:
            note.delete()
        return subject
