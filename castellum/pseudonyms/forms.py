# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


class PseudonymField(forms.CharField):
    def clean(self, value):
        cleaned = super().clean(value)
        try:
            return settings.CASTELLUM_PSEUDONYM_CLEAN(cleaned)
        except ValueError as e:
            raise ValidationError(_('Invalid pseudonym'), code='invalid') from e


class DomainForm(forms.Form):
    domain = forms.ChoiceField(label=_('Pseudonym list'))

    def __init__(self, *args, domains, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['domain'].choices = [(d.key, str(d)) for d in domains]
        if self.fields['domain'].choices:
            self.fields['domain'].initial = self.fields['domain'].choices[0][0]
        else:
            self.fields['domain'].disabled = True
            self.cleaned_data = {}
            self.add_error(None, _('All pseudonym lists have been deleted.'))


class PseudonymForm(DomainForm):
    pseudonym = PseudonymField(label=_('Pseudonym'))
