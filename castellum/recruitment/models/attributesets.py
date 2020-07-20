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

import functools
from collections import OrderedDict

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from parler.managers import TranslatableManager
from parler.models import TranslatableModel
from parler.models import TranslatedFields
from parler.utils.context import switch_language

from castellum.studies.models import StudyType
from castellum.subjects.models import Subject
from castellum.utils.models import TimeStampedModel

from .. import attribute_fields
from ..attribute_fields import ANSWER_DECLINED

UNCATEGORIZED = "UNCATEGORIZED"


@functools.lru_cache(maxsize=2)
def get_description_by_statistics_rank(rank):
    try:
        return AttributeDescription.objects.get(statistics_rank=rank)
    except AttributeDescription.DoesNotExist:
        return None


class ImportMixin:
    def export(self):
        data = {}
        for field in self.import_fields:
            data[field] = getattr(self, field)
        for field in self.import_translated_fields:
            data[field] = {}
        for translation in self.translations.all():
            for field in self.import_translated_fields:
                data[field][translation.language_code] = getattr(translation, field)
        return data

    @classmethod
    def _import(cls, data, **kwargs):
        obj = cls(**kwargs)
        for key in data:
            if key in cls.import_translated_fields:
                for lang, value in data[key].items():
                    with switch_language(obj, lang):
                        setattr(obj, key, value)
            elif key in cls.import_fields:
                setattr(obj, key, data[key])
        obj.save()
        return obj


class AttributeSet(TimeStampedModel):
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE, editable=False)
    data = JSONField(encoder=DjangoJSONEncoder)
    onetime_invitation_disinterest = models.BooleanField(_('One time invitation'), default=False)
    study_type_disinterest = models.ManyToManyField(
        StudyType,
        verbose_name=_('Does not want to participate in the following study types:'),
        blank=True,
        related_name='+',
    )

    class Meta:
        verbose_name = _('Attribute set')
        verbose_name_plural = _('Attribute sets')

    def get_absolute_url(self):
        return reverse('subjects:detail', args=[self.subject.pk])

    def get_data(self):
        qs = AttributeDescription.objects.all()
        return {desc.json_key: desc.field.from_json(self.data.get(desc.json_key)) for desc in qs}

    def get_verbose_name(self, pk):
        description = AttributeDescription.objects.get(pk=pk)
        return description.label

    def get_display(self, pk):
        description = AttributeDescription.objects.get(pk=pk)
        value = self.data.get(description.json_key)
        return description.field.get_display(value)

    def get_field_names(self):
        return AttributeDescription.objects.values_list('pk', flat=True)

    def get_statistics_bucket(self, rank):
        description = get_description_by_statistics_rank(rank)
        if not description:
            return None
        value = description.field.from_json(self.data.get(description.json_key))

        if not value or value == ANSWER_DECLINED:
            return None

        return description.field.get_statistics_bucket(value)

    def get_completeness(self):
        # Needs to match ``filter_queries.completeness_expr()``
        completed = len([k for k, v in self.data.items() if v not in [None, '']])
        total = AttributeDescription.objects.count()
        return completed, total


class AttributeCategory(ImportMixin, TranslatableModel):
    import_fields = ['order']
    import_translated_fields = ['label']

    order = models.IntegerField(default=0)

    translations = TranslatedFields(
        label=models.CharField(max_length=64)
    )

    class Meta:
        ordering = ['order']
        verbose_name = _('Attribute category')
        verbose_name_plural = _('Attribute categories')

    def __str__(self):
        return self.label

    def export(self):
        data = super().export()
        data['descriptions'] = [desc.export() for desc in self.attributedescription_set.all()]
        return data

    @classmethod
    def _import(cls, data):
        category = super()._import(data)
        for description in data.get('descriptions', []):
            AttributeDescription._import(description, category=category)
        return category


class AttributeDescriptionManager(TranslatableManager):
    def allowed_read(self, user, obj=None):
        privacy_level = user.get_privacy_level(obj=obj)
        return self.filter(privacy_level_read__lte=privacy_level)

    def allowed_write(self, user, obj=None):
        privacy_level = user.get_privacy_level(obj=obj)
        return self.filter(privacy_level_write__lte=privacy_level)

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


class AttributeDescription(ImportMixin, TranslatableModel):
    FIELD_TYPE_CHOICES = (
        ('CharField', _('CharField')),
        ('ChoiceField', _('ChoiceField')),
        ('MultipleChoiceField', _('MultipleChoiceField')),
        ('OrderedChoiceField', _('OrderedChoiceField')),
        ('IntegerField', _('IntegerField')),
        ('BooleanField', _('BooleanField')),
        ('DateField', _('DateField')),
        ('AgeField', _('AgeField')),
    )
    STATISTICS_RANK_CHOICES = (
        ('primary', _('primary')),
        ('secondary', _('secondary')),
    )
    STATISTICS_TYPES = ['ChoiceField', 'OrderedChoiceField', 'BooleanField', 'AgeField']

    import_fields = ['field_type', 'privacy_level_read', 'privacy_level_write', 'order']
    import_translated_fields = ['label', '_filter_label', 'help_text']

    translations = TranslatedFields(
        label=models.CharField(max_length=64),
        _filter_label=models.CharField(max_length=64, blank=True, default=''),
        help_text=models.TextField(blank=True, default=''),
    )

    field_type = models.CharField(max_length=64, choices=FIELD_TYPE_CHOICES)
    privacy_level_read = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(2)]
    )
    privacy_level_write = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(2)]
    )
    order = models.IntegerField(default=0)
    category = models.ForeignKey(
        AttributeCategory, on_delete=models.SET_NULL, null=True, blank=True)
    statistics_rank = models.CharField(
        max_length=16, choices=STATISTICS_RANK_CHOICES, null=True, blank=True, unique=True)

    objects = AttributeDescriptionManager()

    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.category:
            return '{}:{}'.format(self.category, self.label)
        return self.label

    def clean(self):
        if self.privacy_level_read > self.privacy_level_write:
            raise ValidationError(
                _('Privacy level for reading may not be higher than for writing.'), code='invalid')

        if self.statistics_rank and self.field_type not in self.STATISTICS_TYPES:
            msg = _('Statistics rank can only be set for the following field types: %s')
            raise ValidationError(msg, code='invalid', params=', '.join(self.STATISTICS_TYPES))

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

    @classmethod
    def get_statistics_buckets(cls, rank):
        description = get_description_by_statistics_rank(rank)
        if not description:
            return [(None, None)]

        return description.field.get_statistics_buckets() + [
            (None, _('Other')),
        ]

    def export(self):
        data = super().export()
        data['choices'] = [choice.export() for choice in self.attributechoice_set.all()]
        return data

    @classmethod
    def _import(cls, data, category=None):
        description = super()._import(data, category=category)
        for index, choice in enumerate(data.get('choices', [])):
            AttributeChoice._import(choice, description=description, order=index * 10)
        return description


class AttributeChoice(ImportMixin, TranslatableModel):
    import_fields = []
    import_translated_fields = ['label']

    description = models.ForeignKey(AttributeDescription, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    translations = TranslatedFields(
        label=models.CharField(max_length=64)
    )

    class Meta:
        ordering = ['order']
