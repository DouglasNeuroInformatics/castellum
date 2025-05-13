# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _


class NewsMailForm(forms.Form):
    subject = forms.CharField(label=_('Email subject'), required=True)
    body = forms.CharField(
        label=_('Email body'),
        help_text=_(
            'Any "{name}"-tags included in the email-body will '
            'automatically be replaced with the full name of the subject.'
        ),
        widget=forms.Textarea,
        required=True,
    )
