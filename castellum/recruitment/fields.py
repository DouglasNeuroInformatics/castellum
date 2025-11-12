# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_VALUES = {
    'years': 200,
    'months': 180,
    'days': 1460,
}


def _get_age_fields():
    return [
        forms.CharField(),
        forms.ChoiceField(choices=[
            ('years', _('years')),
            ('months', _('months')),
            ('days', _('days')),
            ('date', _('date of birth')),
        ]),
    ]


class AgeWidget(forms.MultiWidget):
    template_name = 'recruitment/age_widget.html'

    def __init__(self, attrs=None):
        widgets = [field.widget for field in _get_age_fields()]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return list(value)
        else:
            return [None, None]


class AgeField(forms.MultiValueField):
    widget = AgeWidget

    def __init__(self, **kwargs):
        super().__init__(fields=_get_age_fields(), **kwargs)

    def compress(self, value):
        return tuple(value)

    def clean(self, value):
        period, scale = super().clean(value)
        if scale == 'date':
            field = forms.DateField()
            try:
                date = datetime.date.fromisoformat(period)
            except ValueError as e:
                raise ValidationError('Enter a valid date (YYYY-MM-DD)') from e

            today = datetime.date.today()
            if date + relativedelta(years=15) < today and date.month != 1:
                raise ValidationError(
                    'Please select january 1st for dates far in the past'
                )
            if date + relativedelta(years=4) < today and date.day != 1:
                raise ValidationError(
                    'Please select the first day of the month for dates far in the past'
                )

            return period, scale
        else:
            field = forms.IntegerField(min_value=0, max_value=MAX_VALUES[scale])
            i = field.clean(period)
            return i, scale
