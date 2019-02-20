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

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.utils.forms import DateField
from castellum.utils.forms import IntegerChoiceField

from .fields import AgeField


class BaseAttributeField:
    available_operators = NotImplemented
    form_class = NotImplemented
    filter_form_class = None

    def __init__(self, description):
        self.description = description

    def formfield(self, form_class=None, **kwargs):
        form_class = form_class or self.form_class
        defaults = {
            'label': self.description.label,
            'help_text': self.description.help_text,
            'required': False,
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def filter_formfield(self, **kwargs):
        return self.formfield(self.filter_form_class, **kwargs)

    def filter_to_q(self, operator, value):
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

    def from_json(self, value):
        return value

    def get_display(self, value):
        return self.from_json(value)

    def get_filter_display(self, operator, value):
        operator = dict(self.available_operators)[operator]
        return '{} {} {}'.format(self.description.filter_label, operator, value)


class DateAttributeField(BaseAttributeField):
    form_class = DateField
    available_operators = [
        ("lt", _("before")),
        ("gt", _("after")),
    ]

    def from_json(self, value):
        if value is None:
            return None
        dt = datetime.datetime.strptime(value, '%Y-%m-%d')
        return dt.date()


class NumberAttributeField(BaseAttributeField):
    form_class = forms.IntegerField
    available_operators = [
        ("lt", _("<")),
        ("gt", _(">")),
        ("exact", _("==")),
        ("!exact", _("!=")),
        ("lte", _("<=")),
        ("gte", _(">=")),
    ]


class BooleanAttributeField(BaseAttributeField):
    form_class = forms.NullBooleanField
    available_operators = [
        ("exact", _("is")),
    ]


class TextAttributeField(BaseAttributeField):
    form_class = forms.CharField
    available_operators = [
        ("exact", _("is")),
        ("!exact", _("is not")),
        ("contains", _("contains")),
    ]


class ChoiceAttributeField(BaseAttributeField):
    form_class = IntegerChoiceField
    available_operators = [
        ("exact", _("is")),
        ("!exact", _("is not")),
    ]

    def formfield(self, form_class=None, **kwargs):
        qs = self.description.attributechoice_set.translated()
        choices = [(None, _('Unknown'))] + list(qs.values_list('pk', 'translations__label'))
        return super().formfield(form_class=form_class, choices=choices, **kwargs)

    def get_display(self, value):
        if value is None:
            return None
        choice = self.description.attributechoice_set.get(pk=value)
        return choice.label

    def get_filter_display(self, operator, value):
        value = self.get_display(value)
        return super().get_filter_display(operator, value)


class AgeAttributeField(DateAttributeField):
    SCALES = {
        'years': _('years'),
        'days': _('days'),
    }

    filter_form_class = AgeField
    available_operators = [
        ("lt", _("older than")),
        ("gt", _("younger than")),
    ]

    def filter_to_q(self, operator, value):
        period, scale = value
        try:
            date = datetime.date.today() - relativedelta(**{scale: period})
        except (ValueError, OverflowError):
            date = datetime.date.min
        return super().filter_to_q(operator, date)

    def get_filter_display(self, operator, value):
        period, scale = value
        value = '{} {}'.format(period, self.SCALES[scale])
        return super().get_filter_display(operator, value)
