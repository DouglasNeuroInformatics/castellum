# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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
            ] + settings.CASTELLUM_CUSTOM_PRIVACY_LEVELS)),
        }

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

    def clean(self):
        cleaned_data = super().clean()

        privacy_level = cleaned_data.get('privacy_level', 0)
        if not self.user.has_privacy_level(privacy_level):
            raise ValidationError(
                _("Please choose lower privacy level for the subject."), code='invalid'
            )

        if cleaned_data.get('to_be_deleted') and self.instance.has_consent:
            raise ValidationError(
                _(
                    'Subjects can either be marked for deletion or have recruitment consent, '
                    'not both.'
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
            'not_available_until',
            'source',
        ]
        widgets = {
            'source': DatalistWidget(datalist=(
                Subject.objects.order_by('source').values_list('source', flat=True).distinct
            )),
        }
