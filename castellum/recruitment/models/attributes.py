# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools
from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from parler.managers import TranslatableQuerySet
from parler.models import TranslatableModel
from parler.models import TranslatedFields

from .. import attribute_fields
from ..attribute_fields import ANSWER_DECLINED  # noqa

UNCATEGORIZED = 'UNCATEGORIZED'


@functools.lru_cache(maxsize=2)
def get_attribute_by_statistics_rank(rank):
    try:
        return Attribute.objects.get(statistics_rank=rank)
    except Attribute.DoesNotExist:
        return None


class AttributeCategory(TranslatableModel):
    order = models.IntegerField(default=0)

    translations = TranslatedFields(label=models.CharField(max_length=64))

    class Meta:
        ordering = ['order']
        verbose_name = _('Attribute category')
        verbose_name_plural = _('Attribute categories')

    def __str__(self):
        return self.label


class AttributeQuerySet(TranslatableQuerySet):
    def by_category(self, qs=None):
        qs = qs or self.all()
        qs = qs.select_related('category').order_by('category__order', 'order')

        categories = OrderedDict()
        categories[UNCATEGORIZED] = []
        for attribute in qs:
            category = attribute.category or UNCATEGORIZED
            categories.setdefault(category, [])
            categories[category].append(attribute)
        return categories


class Attribute(TranslatableModel):
    FIELD_TYPE_CHOICES = [
        ('CharField', 'CharField'),
        ('ChoiceField', 'ChoiceField'),
        ('MultipleChoiceField', 'MultipleChoiceField'),
        ('OrderedChoiceField', 'OrderedChoiceField'),
        ('IntegerField', 'IntegerField'),
        ('BooleanField', 'BooleanField'),
        ('DateField', 'DateField'),
        ('AgeField', 'AgeField'),
    ]
    STATISTICS_RANK_CHOICES = [
        ('primary', _('primary')),
        ('secondary', _('secondary')),
    ]
    STATISTICS_TYPES = ['ChoiceField', 'OrderedChoiceField', 'BooleanField', 'AgeField']

    translations = TranslatedFields(
        label=models.CharField(max_length=64),
        _filter_label=models.CharField(max_length=64, blank=True, default=''),
        help_text=models.TextField(blank=True, default=''),
    )

    field_type = models.CharField(max_length=64, choices=FIELD_TYPE_CHOICES)
    url = models.URLField(
        verbose_name=_('URL'),
        help_text=_('URL to a formal definition in an ontology'),
        blank=True,
    )
    order = models.IntegerField(default=0)
    category = models.ForeignKey(
        AttributeCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    statistics_rank = models.CharField(
        max_length=16,
        choices=STATISTICS_RANK_CHOICES,
        null=True,
        blank=True,
        unique=True,
    )

    objects = AttributeQuerySet.as_manager()

    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.category:
            return f'{self.category}:{self.label}'
        return self.label

    def clean(self):
        if self.statistics_rank and self.field_type not in self.STATISTICS_TYPES:
            raise ValidationError(_(
                'Statistics rank can only be set for the following '
                'field types: %(field_types)s',
            ), code='invalid', params={'field_types': ', '.join(self.STATISTICS_TYPES)})

    @cached_property
    def json_key(self):
        # perf: not expensive, but called a lot (e.g. by statistics)
        # can not be a number because then queries like `data__8` would expect an array.
        return f'd{self.pk}'

    @property
    def filter_label(self):
        return self._filter_label or self.label

    @property
    def field(self):
        mapping = {
            'CharField': attribute_fields.TextAttributeField,
            'ChoiceField': attribute_fields.ChoiceAttributeField,
            'MultipleChoiceField': attribute_fields.MultipleChoiceAttributeField,
            'OrderedChoiceField': attribute_fields.OrderedChoiceAttributeField,
            'IntegerField': attribute_fields.NumberAttributeField,
            'BooleanField': attribute_fields.BooleanAttributeField,
            'DateField': attribute_fields.DateAttributeField,
            'AgeField': attribute_fields.AgeAttributeField,
        }
        return mapping[self.field_type](self)


class AttributeChoice(TranslatableModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    translations = TranslatedFields(label=models.CharField(max_length=64))

    class Meta:
        ordering = ['order']
