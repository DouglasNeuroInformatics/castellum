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
    document = ConsentDocument.objects.filter(consent__subject=subject, is_valid=True)
    if document.exists():
        return (document.first().pk, str(document.first()))
    else:
        return 'waiting_for_consent'


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

    consent_status = Consent._meta.get_field('status').formfield(
        label=_('Recruitment consent'),
        help_text=_(
            'Without recruitment consent, this subject will not be taken into account for future '
            'recruitment. Withdrawing recruitment consent has no effect on study consent. '
            'Therefore no data related to existing studies is deleted.'
        ),
        required=False,
    )

    recruitment_consent = forms.ChoiceField(choices=[
            ('waiting_for_consent', _('Waiting for consent')),
        ] + [(document.pk, document) for document in ConsentDocument.objects.filter(is_valid=True)],
        help_text=_(
            'Select whether subjects have recruitment consent or still need to give consent.'
        )
    )

    does_not_want_to_be_recruited = forms.BooleanField(
        label=_("Does not want to be recruited"),
        required=False,
        help_text=Subject._meta.get_field('does_not_want_to_be_recruited').help_text,
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
        self.fields['recruitment_consent'].initial = get_initial_consent_status(self.instance)
        self.fields['does_not_want_to_be_recruited'].initial = self.instance.does_not_want_to_be_recruited  # noqa

        if self.instance.does_not_want_to_be_recruited:
            self.fields['recruitment_consent'].disabled = True

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

    def save_recruitment_consent(self, subject):
        document = self.cleaned_data.get('recruitment_consent')
        if document == 'waiting_for_consent':
            if subject.has_consent:
                subject.consent.status = Consent.WAITING
                subject.consent.save()
        else:
            if subject.has_consent_or_waiting:
                subject.consent.delete()
            document = ConsentDocument.objects.get(pk=document)
            Consent.objects.create(
                subject=subject,
                status=Consent.CONFIRMED,
                underage_when_given=subject.contact.is_underage,
                document=document,
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

        self.instance.does_not_want_to_be_recruited = self.cleaned_data.get(
            'does_not_want_to_be_recruited'
        )
        subject = super().save(*args, **kwargs)
        self.save_recruitment_consent(subject)

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
