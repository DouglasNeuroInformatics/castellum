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

import functools
from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from parler.managers import TranslatableQuerySet
from parler.models import TranslatableModel
from parler.models import TranslatedFields

from .. import attribute_fields
from ..attribute_fields import ANSWER_DECLINED  # noqa

UNCATEGORIZED = "UNCATEGORIZED"


@functools.lru_cache(maxsize=2)
def get_description_by_statistics_rank(rank):
    try:
        return AttributeDescription.objects.get(statistics_rank=rank)
    except AttributeDescription.DoesNotExist:
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


class AttributeDescriptionQuerySet(TranslatableQuerySet):
    def by_category(self, qs=None):
        qs = qs or self.all()
        qs = qs.select_related('category').order_by('category__order', 'order')

        categories = OrderedDict()
        categories[UNCATEGORIZED] = []
        for description in qs:
            category = description.category or UNCATEGORIZED
            categories.setdefault(category, [])
            categories[category].append(description)
        return categories


class AttributeDescription(TranslatableModel):
    FIELD_TYPE_CHOICES = [
        ('CharField', _('CharField')),
        ('ChoiceField', _('ChoiceField')),
        ('MultipleChoiceField', _('MultipleChoiceField')),
        ('OrderedChoiceField', _('OrderedChoiceField')),
        ('IntegerField', _('IntegerField')),
        ('BooleanField', _('BooleanField')),
        ('DateField', _('DateField')),
        ('AgeField', _('AgeField')),
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
        verbose_name=_('URL'), help_text=_('URL to a formal definition in an ontology'), blank=True
    )
    order = models.IntegerField(default=0)
    category = models.ForeignKey(
        AttributeCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    statistics_rank = models.CharField(
        max_length=16, choices=STATISTICS_RANK_CHOICES, null=True, blank=True, unique=True
    )

    objects = AttributeDescriptionQuerySet.as_manager()

    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.category:
            return '{}:{}'.format(self.category, self.label)
        return self.label

    def clean(self):
        if self.statistics_rank and self.field_type not in self.STATISTICS_TYPES:
            raise ValidationError(_(
                'Statistics rank can only be set for the following field types: %(field_types)s',
            ), code='invalid', params={'field_types': ', '.join(self.STATISTICS_TYPES)})

    @property
    def json_key(self):
        # can not be a number because then queries like `data__8` would expect an array.
        return 'd{}'.format(self.pk)

    @property
    def filter_label(self):
        return self._filter_label or self.label

    @property
    def field(self):
        MAPPING = {
            'CharField': attribute_fields.TextAttributeField,
            'ChoiceField': attribute_fields.ChoiceAttributeField,
            'MultipleChoiceField': attribute_fields.MultipleChoiceAttributeField,
            'OrderedChoiceField': attribute_fields.OrderedChoiceAttributeField,
            'IntegerField': attribute_fields.NumberAttributeField,
            'BooleanField': attribute_fields.BooleanAttributeField,
            'DateField': attribute_fields.DateAttributeField,
            'AgeField': attribute_fields.AgeAttributeField,
        }
        return MAPPING[self.field_type](self)


class AttributeChoice(TranslatableModel):
    description = models.ForeignKey(AttributeDescription, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    translations = TranslatedFields(label=models.CharField(max_length=64))

    class Meta:
        ordering = ['order']
