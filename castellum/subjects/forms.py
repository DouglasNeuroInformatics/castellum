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
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Consent
from .models import ConsentConfirmation
from .models import Subject


class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject
        exclude = ()

    consent_type = ConsentConfirmation._meta.get_field('type').formfield(required=False)
    consent_status = ConsentConfirmation._meta.get_field('status').formfield(required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        consent = self.instance.consent
        if consent and consent.status == ConsentConfirmation.WAITING:
            self.fields['consent_type'].initial = consent.type
            self.fields['consent_status'].initial = consent.status

    def clean(self):
        cleaned_data = super().clean()

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(
                _("Please choose lower privacy level for the subject."),
                code='invalid',
            )

        if self.cleaned_data['consent_type'] or self.cleaned_data['consent_status']:
            consent_check = [self.cleaned_data['consent_type'], self.cleaned_data['consent_status']]
            if not all(consent_check):
                raise ValidationError(_("Please, fill out both type and "
                                        "status of the consent."), code='invalid')

        return cleaned_data

    def save(self, commit=True):
        subject = super().save(commit)
        consent = subject.consent
        if consent and consent.status == ConsentConfirmation.WAITING:
            if (
                consent.type != self.cleaned_data['consent_type'] or
                consent.status != self.cleaned_data['consent_status']
            ):
                consent.type = self.cleaned_data['consent_type']
                consent.status = self.cleaned_data['consent_status']
                consent.save()
        elif self.cleaned_data['consent_type'] or self.cleaned_data['consent_status']:
            ConsentConfirmation.objects.create(
                type=self.cleaned_data['consent_type'],
                status=self.cleaned_data['consent_status'],
                subject=subject,
                revision=Consent.objects.latest(),
            )
        return subject


class SubjectPrivacyLevelForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['privacy_level']

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
