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
from django.utils.translation import ugettext as _

from phonenumber_field.formfields import PhoneNumberField as _PhoneNumberFormField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget


class DateInput(forms.DateInput):
    def __init__(self, attrs=None):
        defaults = {
            'placeholder': _('yyyy-mm-dd, e.g. 2018-07-21'),
            'data-widget': 'datepicker',
        }
        if attrs:
            defaults.update(attrs)
        super().__init__(attrs=defaults)


class DateTimeInput(forms.SplitDateTimeWidget):
    template_name = 'utils/widgets/splitdatetime.html'

    def __init__(self, date_attrs=None, time_attrs=None):
        date_defaults = {
            'placeholder': _('yyyy-mm-dd, e.g. 2018-07-21'),
            'data-widget': 'datepicker',
        }
        if date_attrs:
            date_defaults.update(date_attrs)

        time_defaults = {
            'placeholder': _('HH:MM, e.g. 13:00'),
        }
        if time_attrs:
            time_defaults.update(time_attrs)

        super().__init__(date_attrs=date_defaults, time_attrs=time_defaults)


class DateField(forms.DateField):
    widget = DateInput


class DateTimeField(forms.SplitDateTimeField):
    widget = DateTimeInput


class PhoneNumberWidget(PhoneNumberInternationalFallbackWidget):
    def __init__(self, attrs=None):
        defaults = {
            'placeholder': _('e.g. 030 123456'),
        }
        if attrs:
            defaults.update(defaults)
        super().__init__(attrs=defaults)


class PhoneNumberField(_PhoneNumberFormField):
    widget = PhoneNumberWidget
