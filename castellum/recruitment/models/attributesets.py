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
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.pseudonyms.models import SubjectData
from castellum.utils.forms import DateField as DateFormField
from parler.models import TranslatableModel
from parler.models import TranslatedFields
from parler.managers import TranslatableManager

from ..fields import AgeField
from ..utils import get_study_filter_q


class IntegerChoiceField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('coerce', int)
        super().__init__(*args, **kwargs)


class AttributeSet(SubjectData):
    domain = settings.DOMAINS['attributeset']

    data = JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = _('attribute set')
        verbose_name_plural = _('attribute sets')

    def get_absolute_url(self):
        contact_pseudonym = resolve_pseudonym(self.domain, self.pseudonym, Contact.domain)
        return reverse('contacts:detail', args=[contact_pseudonym])

    def get_data(self):
        qs = AttributeDescription.objects.all()
        return {desc.json_key: desc.from_json(self.data.get(desc.json_key)) for desc in qs}

    @classmethod
    def apply_study_filter(cls, study, queryset=None):
        if not queryset:
            queryset = cls.objects
        return queryset.filter(get_study_filter_q(study))

    def get_verbose_name(self, pk):
        description = AttributeDescription.objects.get(pk=pk)
        return description.label

    def get_display(self, pk):
        description = AttributeDescription.objects.get(pk=pk)
        value = description.from_json(self.data.get(description.json_key))
        if value and description.field_type == 'ChoiceField':
            choice = AttributeChoice.objects.get(description=description, pk=value)
            return choice.label
        else:
            return value

    def get_field_names(self):
        return AttributeDescription.objects.values_list('pk', flat=True)


class AttributeDescriptionManager(TranslatableManager):
    def allowed(self, user, obj=None):
        privacy_level = user.get_privacy_level(obj=obj)
        return self.filter(privacy_level__lte=privacy_level)


def date_from_json(value):
    dt = datetime.datetime.strptime(value, '%Y-%m-%d')
    return dt.date()


class AttributeDescription(TranslatableModel):
    FIELD_TYPE_CHOICES = (
        ('CharField', _('CharField')),
        ('ChoiceField', _('ChoiceField')),
        ('IntegerField', _('IntegerField')),
        ('DateField', _('DateField')),
        ('AgeField', _('AgeField')),
    )

    translations = TranslatedFields(
        label = models.CharField(max_length=64),
        _filter_label=models.CharField(max_length=64, blank=True, default=''),
        help_text=models.TextField(blank=True, default=''),
    )

    field_type = models.CharField(max_length=64, choices=FIELD_TYPE_CHOICES)
    privacy_level = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(2)])
    weight = models.IntegerField(default=0)

    objects = AttributeDescriptionManager()

    class Meta:
        ordering = ['weight']

    def __str__(self):
        return self.label

    @property
    def json_key(self):
        # can not be a number because then queries like `data__8` would expect an array.
        return 'd{}'.format(self.pk)

    @property
    def filter_label(self):
        return self._filter_label or self.label

    def get_form_field(self, form_class=None):
        kwargs = {
            'label': self.label,
            'help_text': self.help_text,
            'required': False,
        }

        if not form_class:
            MAPPING = {
                'CharField': forms.CharField,
                'ChoiceField': IntegerChoiceField,
                'IntegerField': forms.IntegerField,
                'DateField': DateFormField,
                'AgeField': DateFormField,
            }
            form_class = MAPPING[self.field_type]

        if self.field_type == 'ChoiceField':
            kwargs['choices'] = list(self.attributechoice_set.
                                     translated().values_list('pk', 'translations__label'))

        return form_class(**kwargs)

    def get_filter_field(self):
        MAPPING = {
            'CharField': TextFilterField,
            'ChoiceField': TextFilterField,
            'IntegerField': NumberFilterField,
            'DateField': DateFilterField,
            'AgeField': AgeFilterField,
        }
        return MAPPING[self.field_type]()

    def from_json(self, value):
        MAPPING = {
            'DateField': date_from_json,
            'AgeField': date_from_json,
        }
        if value is not None and self.field_type in MAPPING:
            return MAPPING[self.field_type](value)
        return value


class AttributeChoice(TranslatableModel):
    description = models.ForeignKey(AttributeDescription, on_delete=models.CASCADE)
    translations = TranslatedFields(
        label=models.CharField(max_length=64)
    )


class BaseFilterField:
    available_operators = NotImplemented

    def formfield(self, description, **kwargs):
        return description.get_form_field(**kwargs)

    def to_q(self, description, operator, value):
        field_name = 'data__' + description.json_key
        if operator.startswith('!'):
            key = '{}__{}'.format(field_name, operator[1:])
            q = models.Q(**{key: value})
            q_empty = models.Q(**{field_name: ''})
            q_null = models.Q(**{field_name: None})
            return ~q & ~q_empty & ~q_null
        else:
            key = '{}__{}'.format(field_name, operator)
            return models.Q(**{key: value})

    def to_str(self, description, operator, value):
        operator = dict(self.available_operators)[operator]
        if description.field_type == 'ChoiceField':
            choice = AttributeChoice.objects.get(description=description, pk=value)
            value = choice.label
        return '{} {} {}'.format(description.filter_label, operator, value)


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

    def formfield(self, description, **kwargs):
        kwargs.setdefault('form_class', AgeField)
        return super().formfield(description, **kwargs)

    def to_q(self, description, operator, value):
        period, scale = value
        try:
            date = datetime.date.today() - relativedelta(**{scale: period})
        except (ValueError, OverflowError):
            date = datetime.date.min
        return super().to_q(description, operator, date)

    def to_str(self, description, operator, value):
        period, scale = value
        value = '{} {}'.format(period, self.SCALES[scale])
        return super().to_str(description, operator, value)
