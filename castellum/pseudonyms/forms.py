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


class DomainForm(forms.Form):
    domain = forms.ChoiceField(label=_('Domain'))

    def __init__(self, *args, domains, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['domain'].choices = [(d.key, str(d)) for d in domains]
        if self.fields['domain'].choices:
            self.fields['domain'].initial = self.fields['domain'].choices[0][0]
        else:
            self.fields['domain'].disabled = True
            self.cleaned_data = {}
            self.add_error(None, _('All pseudonym domains have been deleted.'))


class PseudonymForm(DomainForm):
    pseudonym = PseudonymField(label=_('Pseudonym'))
