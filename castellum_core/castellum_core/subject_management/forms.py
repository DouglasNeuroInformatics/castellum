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
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from .models import Subject


class SubjectForm(forms.ModelForm):

    phone_number = PhoneNumberField(label=_("Phone number"))
    phone_number_alternative = PhoneNumberField(label=_("Alternative phone number"))

    class Meta:
        model = Subject
        fields = '__all__'

        widgets = {
            'phone_number': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Phone (ex. +4917693333333)')}),
            'phone_number_alternative': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Alternative phone (ex. +4917693333333)')}),
        }
