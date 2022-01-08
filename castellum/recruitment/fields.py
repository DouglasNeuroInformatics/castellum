# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
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
from django.utils.translation import gettext_lazy as _


def _get_age_fields():
    return [
        forms.IntegerField(error_messages={}, min_value=0, max_value=1000),
        forms.ChoiceField(choices=[
            ('years', _('years')),
            ('months', _('months')),
            ('days', _('days')),
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
