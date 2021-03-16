# (c) 2018-2021
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
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


class PseudonymField(forms.CharField):
    def clean(self, value):
        cleaned = super().clean(value)
        try:
            return settings.CASTELLUM_PSEUDONYM_CLEAN(cleaned)
        except ValueError:
            raise ValidationError(_('Invalid pseudonym'), code='invalid')


class PseudonymForm(forms.Form):
    domain = forms.ChoiceField(label=_('Domain'))
    pseudonym = PseudonymField(label=_('Pseudonym'))

    def __init__(self, *args, context, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['domain'].choices = [
            (d.key, d.key) for d in context.domains.all()
        ]
