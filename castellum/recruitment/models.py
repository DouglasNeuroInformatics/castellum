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

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from picklefield.fields import PickledObjectField

from castellum.pseudonyms.models import SubjectData
from castellum.studies.models import Study
from castellum.utils.fields import DateField
from castellum.utils.fields import DateTimeField

from .fields import AgeField


class AttributeSet(SubjectData):
    domain = settings.DOMAINS['attributeset']

    filter_fields = {
        'date_of_birth': 'AgeFilterField',
    }
    filter_names = {
        'date_of_birth': _('age'),
    }

    handedness = models.CharField(_('handedness'), blank=True, max_length=10, choices=(
        ('left', _('left')),
        ('right', _('right')),
    ))
    first_language = models.CharField(_('first Language'), blank=True, max_length=5)
    date_of_birth = DateField(_('date of birth'), null=True, blank=True)

    class Meta:
        verbose_name = _('attribute set')
        verbose_name_plural = _('attribute sets')

    def get_absolute_url(self):
        return reverse('recruitment:attributes_detail', args=[self.pseudonym])

    @classmethod
    def apply_study_filter(cls, study, queryset=None):
        if not queryset:
            queryset = cls.objects
        q = models.Q()
        for group in study.subjectfiltergroup_set.all():
            q |= group.to_q()
        return queryset.filter(q)


class ParticipationRequestManager(models.Manager):
    def filter_not_contacted(self, **kwargs):
        return self.get_queryset().filter(status=ParticipationRequest.NOT_CONTACTED, **kwargs)

    def filter_not_reached(self, **kwargs):
        return self.get_queryset().filter(status=ParticipationRequest.NOT_REACHED, **kwargs)


class ParticipationRequest(SubjectData):
    NOT_CONTACTED = 0
    NOT_REACHED = 1
    UNSUITABLE = 2
    INVITED = 3
    STATUS_OPTIONS = (
        (NOT_CONTACTED, _('not contacted')),
        (NOT_REACHED, _('not reached')),
        (UNSUITABLE, _('unsuitable')),
        (INVITED, _('invited')),
    )

    objects = ParticipationRequestManager()

    study = models.ForeignKey(Study, verbose_name=_('study'), on_delete=models.CASCADE)

    status = models.IntegerField(
        _('status of participation request'), choices=STATUS_OPTIONS, default=NOT_CONTACTED)
    updated_at = DateTimeField(_('last updated at'), blank=True, null=True)

    class Meta:
        verbose_name = _('participation request')
        verbose_name_plural = _('participation requests')

    @classmethod
    def get_by_pseudonym(cls, domain, pseudonym):
        return cls.objects.get(study__domain=domain, pseudonym=pseudonym)


class SubjectFilterGroup(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('recruitment:filtergroup_update', args=[self.study.pk, self.pk])

    def to_q(self):
        q = models.Q()
        for f in self.subjectfilter_set.all():
            q &= f.to_q()
        return q

    def get_subject_count(self):
        return AttributeSet.objects.filter(self.to_q()).count()

    def duplicate(self):
        clone = SubjectFilterGroup.objects.create(study=self.study)
        for f in self.subjectfilter_set.all():
            SubjectFilter.objects.create(
                group=clone, field_name=f.field_name, operator=f.operator, value=f.value)
        return clone


class SubjectFilter(models.Model):
    group = models.ForeignKey(SubjectFilterGroup, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=256)
    operator = models.CharField(max_length=64)
    value = PickledObjectField(editable=True)

    def to_q(self):
        filter_field = get_filter_field(self.field_name)
        return filter_field.to_q(self.field_name, self.operator, self.value)

    def get_subject_count(self):
        return AttributeSet.objects.filter(self.to_q()).count()

    def __str__(self):
        filter_field = get_filter_field(self.field_name)
        return filter_field.to_str(self.field_name, self.operator, self.value)


class BaseFilterField:
    available_operators = NotImplemented

    def formfield(self, field_name, **kwargs):
        model_field = AttributeSet._meta.get_field(field_name)
        return model_field.formfield(**kwargs)

    def to_q(self, field_name, operator, value):
        if operator.startswith('!'):
            key = '{}__{}'.format(field_name, operator[1:])
            q = models.Q(**{key: value})
            q_empty = models.Q(**{field_name: ''})
            q_null = models.Q(**{field_name: None})
            return ~q & ~q_empty & ~q_null
        else:
            key = '{}__{}'.format(field_name, operator)
            return models.Q(**{key: value})

    def to_str(self, field_name, operator, value):
        model_field = AttributeSet._meta.get_field(field_name)
        filter_name = AttributeSet.filter_names.get(field_name, model_field.verbose_name)
        operator = dict(self.available_operators)[operator]
        if model_field.choices:
            value = dict(model_field.choices)[value]
        return '{} {} {}'.format(filter_name, operator, value)


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

    def formfield(self, field_name, **kwargs):
        kwargs.setdefault('form_class', AgeField)
        return super().formfield(field_name, **kwargs)

    def to_q(self, field_name, operator, value):
        period, scale = value
        try:
            date = datetime.date.today() - relativedelta(**{scale: period})
        except (ValueError, OverflowError):
            date = datetime.date.min
        return super().to_q(field_name, operator, date)

    def to_str(self, field_name, operator, value):
        period, scale = value
        value = '{} {}'.format(period, self.SCALES[scale])
        return super().to_str(field_name, operator, value)


def get_filter_field(field_name):
    if field_name in AttributeSet.filter_fields:
        FILTERS = {
            "DateFilterField": DateFilterField(),
            "NumberFilterField": NumberFilterField(),
            "TextFilterField": TextFilterField(),
            "AgeFilterField": AgeFilterField(),
        }

        overwrite = AttributeSet.filter_fields[field_name]
        return FILTERS[overwrite]
    else:
        FILTER_MAPPING = {
            "CharField": TextFilterField(),
            "DateField": DateFilterField(),
            "FloatField": NumberFilterField(),
            "IntegerField": NumberFilterField(),
        }

        model_field = AttributeSet._meta.get_field(field_name)
        model_type = model_field.get_internal_type()
        return FILTER_MAPPING[model_type]
