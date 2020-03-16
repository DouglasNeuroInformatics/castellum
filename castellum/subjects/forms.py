# (c) 2018-2020
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

import datetime

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from castellum.utils.forms import DatalistWidget

from .models import Consent
from .models import ConsentDocument
from .models import Subject


class DataProtectionForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ('privacy_level', 'no_recruitment')
        widgets = {
            'privacy_level': forms.RadioSelect,
            'source': DatalistWidget(datalist=(
                Subject.objects.order_by('source').values_list('source', flat=True).distinct
            )),
        }

    consent_type = Consent._meta.get_field('type').formfield(required=False)
    consent_status = Consent._meta.get_field('status').formfield(required=False)
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

        consent = self.instance.consent
        if consent and consent.status == Consent.WAITING:
            self.fields['consent_type'].initial = consent.type
            self.fields['consent_status'].initial = consent.status

        self.fields['to_be_deleted'].initial = self.instance.to_be_deleted
        self.fields['export_requested'].initial = self.instance.export_requested

    def clean(self):
        cleaned_data = super().clean()

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(
                _("Please choose lower privacy level for the subject."), code='invalid'
            )

        consent_check = [self.cleaned_data['consent_type'], self.cleaned_data['consent_status']]
        if any(consent_check) and not all(consent_check):
            raise ValidationError(
                _("Please, fill out both type and status of the consent."), code='invalid'
            )

        if self.cleaned_data.get('to_be_deleted') and not self.instance.to_be_deleted:
            self.instance.to_be_deleted = datetime.date.today()
        elif not self.cleaned_data.get('to_be_deleted') and self.instance.to_be_deleted:
            self.instance.to_be_deleted = None

        if self.cleaned_data.get('export_requested') and not self.instance.export_requested:
            self.instance.export_requested = datetime.date.today()
        elif not self.cleaned_data.get('export_requested') and self.instance.export_requested:
            self.instance.export_requested = None

        return cleaned_data

    def save(self, commit=True):
        subject = super().save(commit)
        consent = subject.consent
        if consent and consent.status == Consent.WAITING:
            if (
                consent.type != self.cleaned_data['consent_type'] or
                consent.status != self.cleaned_data['consent_status']
            ):
                consent.type = self.cleaned_data['consent_type']
                consent.status = self.cleaned_data['consent_status']
                consent.save()
        elif self.cleaned_data['consent_type'] or self.cleaned_data['consent_status']:
            Consent.objects.create(
                type=self.cleaned_data['consent_type'],
                status=self.cleaned_data['consent_status'],
                subject=subject,
                document=ConsentDocument.objects.filter(is_current=True).latest(),
            )
        return subject


class SubjectPrivacyLevelForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['privacy_level']
        widgets = {
            'privacy_level': forms.RadioSelect,
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
