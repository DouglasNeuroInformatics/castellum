# (c) 2018-2020
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
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.utils.forms import DateField
from castellum.utils.forms import IntegerChoiceField
from castellum.utils.forms import IntegerMultipleChoiceField

from .fields import AgeField

ANSWER_DECLINED = "ANSWER_DECLINED"


class BaseAttributeField:
    available_operators: List[Tuple[str, str]]
    form_class: Type[forms.Field]
    filter_form_class: Optional[Type[forms.Field]] = None

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

    def _filter_to_q(self, operator, value):
        field_name = 'attributes__' + self.description.json_key
        key = '{}__{}'.format(field_name, operator)
        return models.Q(**{key: value})

    def filter_to_q(self, operator, value, include_unknown=True):
        field_name = 'attributes__' + self.description.json_key
        inverse = operator.startswith('!')
        if inverse:
            operator = operator[1:]
        q = self._filter_to_q(operator, value)
        q_unknown = (
            models.Q(**{field_name: ''}) |
            models.Q(**{field_name: None}) |
            models.Q(**{field_name + '__isnull': True})
        )

        if inverse:
            if include_unknown:
                return ~q
            else:
                return ~q & ~q_unknown
        else:
            if include_unknown:
                return q | q_unknown
            else:
                return q

    def get_display(self, value):
        if value is None:
            return '—'
        elif value is ANSWER_DECLINED:
            return _('Declined to answer')
        else:
            return value

    def get_filter_display(self, operator, value):
        operator = dict(self.available_operators)[operator]
        return '{} {} {}'.format(self.description.filter_label, operator, value)

    def get_statistics_grouping(self):
        raise NotImplementedError


class DateAttributeField(BaseAttributeField):
    form_class = DateField
    available_operators = [
        ("lt", _("before")),
        ("gt", _("after")),
    ]

    def parse_date(self, value):
        dt = datetime.datetime.strptime(value, '%Y-%m-%d')
        return dt.date()

    def get_display(self, value):
        if not value:
            return super().get_display(None)
        if value == ANSWER_DECLINED:
            return super().get_display(value)
        return self.parse_date(value)


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

    def get_statistics_grouping(self):
        buckets = [
            (True, _('Yes')),
            (False, _('No')),
            (None, _('Other')),
        ]

        def get_bucket(value):
            if value in [ANSWER_DECLINED, '']:
                return None
            return value

        return buckets, get_bucket


class TextAttributeField(BaseAttributeField):
    form_class = forms.CharField
    available_operators = [
        ("exact", _("is")),
        ("!exact", _("is not")),
        ("icontains", _("contains")),
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
        if value in [None, ANSWER_DECLINED]:
            return super().get_display(value)
        choice = self.description.attributechoice_set.get(pk=value)
        return choice.label

    def get_filter_display(self, operator, value):
        value = self.get_display(value)
        return super().get_filter_display(operator, value)

    def get_statistics_grouping(self):
        buckets = [
            (choice.pk, choice.label) for choice in self.description.attributechoice_set.all()
        ] + [
            (None, _('Other')),
        ]

        def get_bucket(value):
            if value in [ANSWER_DECLINED, '']:
                return None
            return value

        return buckets, get_bucket


class MultipleChoiceAttributeField(ChoiceAttributeField):
    form_class = IntegerMultipleChoiceField
    filter_form_class = IntegerChoiceField
    available_operators = [
        ("contains", _("contains")),
        ("!contains", _("does not contain")),
    ]

    def get_display(self, value):
        if not value:
            return super().get_display(None)
        if value == ANSWER_DECLINED:
            return super().get_display(value)
        if not isinstance(value, list):
            value = [value]
        s = super()
        return ', '.join(s.get_display(v) for v in value)


class OrderedChoiceAttributeField(ChoiceAttributeField):
    available_operators = ChoiceAttributeField.available_operators + [
        ("gte", _("is at least")),
        ("lte", _("is at most")),
    ]

    def _filter_to_q(self, operator, value):
        if operator in ['gte', 'lte']:
            threshold = self.description.attributechoice_set.get(pk=value)
            allowed_choices = self.description.attributechoice_set.filter(**{
                'order__' + operator: threshold.order
            })
            # JSONField cannot use `in` lookups
            q = models.Q()
            for choice in allowed_choices:
                q |= models.Q(**{'attributes__' + self.description.json_key: choice.pk})
            return q
        return super()._filter_to_q(operator, value)


class AgeAttributeField(DateAttributeField):
    SCALES = {
        'years': _('years'),
        'months': _('months'),
        'days': _('days'),
    }

    filter_form_class = AgeField
    available_operators = [
        ("lt", _("older than")),
        ("gt", _("younger than")),
    ]

    def _filter_to_q(self, operator, value):
        period, scale = value
        try:
            date = datetime.date.today() - relativedelta(**{scale: period})
        except (ValueError, OverflowError):
            date = datetime.date.min
        return super()._filter_to_q(operator, date)

    def get_filter_display(self, operator, value):
        period, scale = value
        value = '{} {}'.format(period, self.SCALES[scale])
        return super().get_filter_display(operator, value)

    def get_statistics_grouping(self):
        buckets = [
            ('<18', '<18'),
            ('18-25', '18-25'),
            ('26-30', '26-30'),
            ('31-35', '31-35'),
            ('36-40', '36-40'),
            ('41-45', '41-45'),
            ('46-50', '46-50'),
            ('51-55', '51-55'),
            ('56-60', '56-60'),
            ('61-65', '61-65'),
            ('66-70', '66-70'),
            ('>70', '>70'),
            (None, _('Other'))
        ]

        def get_bucket(value):
            if not value or value == ANSWER_DECLINED:
                return None
            value = self.parse_date(value)
            today = datetime.date.today()
            if today < value + relativedelta(years=18):
                return '<18'
            if today < value + relativedelta(years=25):
                return '18-25'
            for y in range(26, 70, 5):
                if today < value + relativedelta(years=y + 5):
                    return '{}-{}'.format(y, y + 4)
            return '>70'

        return buckets, get_bucket
