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

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta

from .fields import AgeField


class BaseFilterField:
    available_operators = NotImplemented

    def __init__(self, description):
        self.description = description

    def formfield(self, **kwargs):
        return self.description.get_form_field(**kwargs)

    def to_q(self, operator, value):
        field_name = 'data__' + self.description.json_key
        if operator.startswith('!'):
            key = '{}__{}'.format(field_name, operator[1:])
            q = models.Q(**{key: value})
            q_empty = models.Q(**{field_name: ''})
            q_null = models.Q(**{field_name: None})
            return ~q & ~q_empty & ~q_null
        else:
            key = '{}__{}'.format(field_name, operator)
            return models.Q(**{key: value})

    def to_str(self, operator, value):
        operator = dict(self.available_operators)[operator]
        if self.description.field_type == 'ChoiceField':
            choice = self.description.attributechoice_set.get(pk=value)
            value = choice.label
        return '{} {} {}'.format(self.description.filter_label, operator, value)


class DateFilterField(BaseFilterField):
    available_operators = [
        ("lt", _("before")),
        ("gt", _("after")),
    ]


class NumberFilterField(BaseFilterField):
    available_operators = [
        ("lt", _("<")),
        ("gt", _(">")),
        ("exact", _("==")),
        ("!exact", _("!=")),
        ("lte", _("<=")),
        ("gte", _(">=")),
    ]


class BooleanFilterField(BaseFilterField):
    available_operators = [
        ("exact", _("is")),
    ]


class TextFilterField(BaseFilterField):
    available_operators = [
        ("exact", _("is")),
        ("!exact", _("is not")),
        ("contains", _("contains")),
    ]


class AgeFilterField(BaseFilterField):
    SCALES = {
        'years': _('years'),
        'days': _('days'),
    }

    available_operators = [
        ("lt", _("older than")),
        ("gt", _("younger than")),
    ]

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', AgeField)
        return super().formfield(**kwargs)

    def to_q(self, operator, value):
        period, scale = value
        try:
            date = datetime.date.today() - relativedelta(**{scale: period})
        except (ValueError, OverflowError):
            date = datetime.date.min
        return super().to_q(operator, date)

    def to_str(self, operator, value):
        period, scale = value
        value = '{} {}'.format(period, self.SCALES[scale])
        return super().to_str(operator, value)
