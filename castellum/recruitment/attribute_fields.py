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

import datetime
import math

from dateutil.relativedelta import relativedelta
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.utils.expressions import ListContainsLookup  # noqa
from castellum.utils.forms import DateField
from castellum.utils.forms import IntegerChoiceField
from castellum.utils.forms import IntegerMultipleChoiceField
from castellum.utils.forms import Select2Mixin

from .fields import AgeField

ANSWER_DECLINED = 'ANSWER_DECLINED'


class Select2IntegerMultipleChoiceField(Select2Mixin, IntegerMultipleChoiceField):
    pass


class BaseAttributeField:
    filter_form_class = None

    def __init__(self, instance):
        self.instance = instance

    def formfield(self, form_class=None, **kwargs):
        form_class = form_class or self.form_class
        defaults = {
            'label': self.instance.label,
            'help_text': self.instance.help_text,
            'required': False,
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def filter_formfield(self, **kwargs):
        return self.formfield(self.filter_form_class, **kwargs)

    def _filter_to_q(self, operator, value):
        field_name = 'attributes__' + self.instance.json_key
        key = f'{field_name}__{operator}'
        return models.Q(**{key: value})

    def filter_to_q(self, operator, value, include_unknown=True):
        field_name = 'attributes__' + self.instance.json_key
        inverse = operator.startswith('!')
        if inverse:
            operator = operator[1:]
        q = self._filter_to_q(operator, value)
        q_unknown = (
            models.Q(**{field_name: ''})
            | models.Q(**{field_name: None})
            | models.Q(**{field_name + '__isnull': True})
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
        if value in ['', None]:
            return '—'
        elif value is ANSWER_DECLINED:
            return _('Declined to answer')
        else:
            return value

    def get_filter_display(self, operator, value):
        operator = dict(self.available_operators)[operator]
        return f'{self.instance.filter_label} {operator} {value}'

    def get_statistics_grouping(self, study):
        raise NotImplementedError


class DateAttributeField(BaseAttributeField):
    form_class = DateField
    available_operators = [
        ('lt', _('before')),
        ('gt', _('after')),
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
        ('lt', _('<')),
        ('gt', _('>')),
        ('exact', _('==')),
        ('!exact', _('!=')),
        ('lte', _('<=')),
        ('gte', _('>=')),
    ]


class BooleanAttributeField(BaseAttributeField):
    form_class = forms.NullBooleanField
    available_operators = [
        ('exact', _('is')),
    ]

    def get_statistics_grouping(self, study):
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
        ('exact', _('is')),
        ('!exact', _('is not')),
        ('icontains', _('contains')),
    ]


class BaseChoiceAttributeField(BaseAttributeField):
    def get_choices(self):
        qs = self.instance.attributechoice_set.all()
        return [(c.pk, c.label) for c in qs]

    def formfield(self, form_class=None, **kwargs):
        return super().formfield(
            form_class=form_class, choices=self.get_choices(), **kwargs
        )

    def get_display(self, value):
        if value in ['', None, ANSWER_DECLINED]:
            return super().get_display(value)
        choice = self.instance.attributechoice_set.get(pk=value)
        return choice.label

    def get_filter_display(self, operator, value):
        value = self.get_display(value)
        return super().get_filter_display(operator, value)

    def get_statistics_grouping(self, study):
        buckets = [
            (choice.pk, choice.label)
            for choice in self.instance.attributechoice_set.all()
        ] + [
            (None, _('Other')),
        ]

        def get_bucket(value):
            if value in [ANSWER_DECLINED, '']:
                return None
            return value

        return buckets, get_bucket


class ChoiceAttributeField(BaseChoiceAttributeField):
    form_class = IntegerChoiceField
    available_operators = [
        ('exact', _('is')),
        ('!exact', _('is not')),
    ]

    def get_choices(self):
        return [(None, _('Unknown')), *super().get_choices()]


class MultipleChoiceAttributeField(BaseChoiceAttributeField):
    form_class = Select2IntegerMultipleChoiceField
    filter_form_class = IntegerChoiceField
    available_operators = [
        # see castellum.utils.expressions.ListContainsLookup
        ('contains', _('contains')),
        ('!contains', _('does not contain')),
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
    available_operators = [
        *ChoiceAttributeField.available_operators,
        ('gte', _('is at least')),
        ('lte', _('is at most')),
    ]

    def _filter_to_q(self, operator, value):
        if operator in ['gte', 'lte']:
            threshold = self.instance.attributechoice_set.get(pk=value)
            allowed_choices = self.instance.attributechoice_set.filter(**{
                'order__' + operator: threshold.order
            })
            # JSONField cannot use `in` lookups
            q = models.Q()
            for choice in allowed_choices:
                q |= models.Q(**{'attributes__' + self.instance.json_key: choice.pk})
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
        ('lt', _('is at least')),
        ('gt', _('younger than')),
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
        value = f'{period} {self.SCALES[scale]}'
        return super().get_filter_display(operator, value)

    def _get_min_date(self, study):
        """Get minimum date of birth allowed by study filters."""

        today = datetime.date.today()

        total = []
        for group in study.subjectfiltergroup_set.all():
            filters = list(group.subjectfilter_set.filter(
                operator='gt', attribute=self.instance
            ))
            if filters:
                dates = [
                    today - relativedelta(**{f.value[1]: f.value[0]})
                    for f in filters
                ]
                # Filters within a group are combined with AND.
                total.append(max(dates))
            else:
                # If any group is not restricted at all, ignore the other groups.
                return None

        if total:
            # Filter groups are combined with OR.
            return min(total)
        else:
            # If there are no filters, there is no restriction.
            return None

    def get_statistics_grouping(self, study):
        today = datetime.date.today()
        min_date = self._get_min_date(study)

        if min_date and min_date >= today - relativedelta(years=2):
            scale = 'months'
            buckets = [(i, str(i)) for i in range(0, 24)]
        elif min_date and min_date >= today - relativedelta(years=18):
            scale = 'years'
            buckets = [(i, str(i)) for i in range(0, 18)]
        else:
            scale = 'years'
            buckets = [
                (17, '<18'),
                (25, '18-25'),
                (30, '26-30'),
                (35, '31-35'),
                (40, '36-40'),
                (45, '41-45'),
                (50, '46-50'),
                (55, '51-55'),
                (60, '56-60'),
                (65, '61-65'),
                (70, '66-70'),
                (math.inf, '>70'),
            ]

        def get_bucket(value):
            if not value or value == ANSWER_DECLINED:
                return None
            value = self.parse_date(value)
            today = datetime.date.today()
            for period, _label in buckets:
                if (
                    period is math.inf
                    or today - relativedelta(**{scale: period + 1}) < value
                ):
                    return period

        return [*buckets, (None, _('Other'))], get_bucket
