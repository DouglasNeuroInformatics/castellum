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

        return cleaned_data

    def save(self, commit=True):
        if not self.cleaned_data.get('to_be_deleted'):
            self.instance.to_be_deleted = None
        elif not self.instance.to_be_deleted:
            self.instance.to_be_deleted = datetime.date.today()

        if not self.cleaned_data.get('export_requested'):
            self.instance.export_requested = None
        elif not self.instance.export_requested:
            self.instance.export_requested = datetime.date.today()

        subject = super().save(commit)

        if subject.consent and subject.consent.status == Consent.WAITING:
            if subject.consent.status != self.cleaned_data['consent_status']:
                subject.consent.status = self.cleaned_data['consent_status']
                subject.consent.save()
        elif self.cleaned_data['consent_status']:
            try:
                document = ConsentDocument.objects.filter(is_valid=True).latest()
            except ConsentDocument.DoesNotExist:
                document = ConsentDocument.objects.create()
            Consent.objects.create(
                status=self.cleaned_data['consent_status'],
                subject=subject,
                document=document,
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
