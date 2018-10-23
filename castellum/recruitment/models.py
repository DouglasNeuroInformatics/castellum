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
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from picklefield.fields import PickledObjectField

from castellum.pseudonyms.models import SubjectData
from castellum.studies.models import Study
from castellum.utils.fields import DateTimeField
from castellum.utils.forms import DateField as DateFormField

from .fields import AgeField


def get_study_filter_q(study):
    q = models.Q()
    for group in study.subjectfiltergroup_set.all():
        q |= group.to_q()
    return q


class AttributeSet(SubjectData):
    domain = settings.DOMAINS['attributeset']

    data = JSONField(encoder=DjangoJSONEncoder)

    class Meta:
        verbose_name = _('attribute set')
        verbose_name_plural = _('attribute sets')

    def get_absolute_url(self):
        return reverse('recruitment:attributes_detail', args=[self.pseudonym])

    @classmethod
    def apply_study_filter(cls, study, queryset=None):
        if not queryset:
            queryset = cls.objects
        return queryset.filter(get_study_filter_q(study))


class AttributeField(models.Model):
    FIELD_TYPE_CHOICES = (
        ('CharField', _('CharField')),
        ('IntegerField', _('IntegerField')),
        ('DateField', _('DateField')),
        ('AgeField', _('AgeField')),
    )

    name = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=64)
    _filter_label = models.CharField(max_length=64, blank=True, default='')
    field_type = models.CharField(max_length=64, choices=FIELD_TYPE_CHOICES)
    weight = models.IntegerField(default=0)

    class Meta:
        ordering = ['weight']

    def __str__(self):
        return self.label

    @property
    def filter_label(self):
        return self._filter_label or self.label

    def get_form_field(self, form_class=None):
        if form_class:
            return form_class(label=self.label, required=False)
        else:
            MAPPING = {
                'CharField': forms.CharField,
                'IntegerField': forms.IntegerField,
                'DateField': DateFormField,
                'AgeField': DateFormField,
            }
            return MAPPING[self.field_type](label=self.label, required=False)

    def get_filter_field(self):
        MAPPING = {
            'CharField': TextFilterField,
            'IntegerField': NumberFilterField,
            'DateField': DateFilterField,
            'AgeField': AgeFilterField,
        }
        return MAPPING[self.field_type]()


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

    class Meta:
        verbose_name = _('participation request')
        verbose_name_plural = _('participation requests')

    @classmethod
    def get_by_pseudonym(cls, domain, pseudonym):
        return cls.objects.get(study__domain=domain, pseudonym=pseudonym)

    @property
    def latest(self):
        return self.revisions.order_by('-created_at')[0]

    @property
    def tries(self):
        return self.revisions.filter(status=ParticipationRequest.NOT_REACHED).count()

    @property
    def updated_at(self):
        return self.latest.created_at

    def get_revisions_display(self):
        return ', '.join(str(r) for r in self.revisions.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ParticipationRequestRevision.objects.create(current=self, status=self.status)


class ParticipationRequestRevision(models.Model):
    """Revision history for ParticipationRequest.

    Each time a ParticipationRequest is saved, an instance of ParticipationRequestRevision
    if created. This way, we have a history of the ParticipationRequest.

    The history is saved in separate model because of these reasons:

    -   ``ParticipationRequest.pseudonym`` is unique.
    -   Saving the history in the same ParticipationRequest model would degrade
        performance because the table would be filled up with old revision.
    """

    current = models.ForeignKey(
        ParticipationRequest, related_name='revisions', on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=ParticipationRequest.STATUS_OPTIONS, default=ParticipationRequest.NOT_CONTACTED)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.created_at, self.get_status_display())


class SubjectFilterGroupManager(models.Manager):
    def clone(self, original_group):
        cloned_group = SubjectFilterGroup.objects.create(study=original_group.study)
        SubjectFilter.objects.bulk_create(self.clone_filters(original_group, cloned_group))
        return cloned_group

    def clone_filters(self, original_group, cloned_group):
        for f in original_group.subjectfilter_set.all():
            yield SubjectFilter(group=cloned_group, field=f.field, operator=f.operator,
                                value=f.value)


class SubjectFilterGroup(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)

    objects = SubjectFilterGroupManager()

    def get_absolute_url(self):
        return reverse('recruitment:filtergroup_update', args=[self.study.pk, self.pk])

    def to_q(self):
        q = models.Q()
        for f in self.subjectfilter_set.all():
            q &= f.to_q()
        return q

    def get_subject_count(self):
        return AttributeSet.objects.filter(self.to_q()).count()


class SubjectFilter(models.Model):
    group = models.ForeignKey(SubjectFilterGroup, on_delete=models.CASCADE)
    field = models.ForeignKey(AttributeField, on_delete=models.CASCADE)
    operator = models.CharField(max_length=64)
    value = PickledObjectField(editable=True)

    def to_q(self):
        filter_field = self.field.get_filter_field()
        return filter_field.to_q(self.field.name, self.operator, self.value)

    def get_subject_count(self):
        return AttributeSet.objects.filter(self.to_q()).count()


class BaseFilterField:
    available_operators = NotImplemented

    def formfield(self, field_name, **kwargs):
        attribute_field = AttributeField.objects.get(name=field_name)
        return attribute_field.get_form_field(**kwargs)

    def to_q(self, field_name, operator, value):
        if operator.startswith('!'):
            key = 'data__{}__{}'.format(field_name, operator[1:])
            q = models.Q(**{key: value})
            q_empty = models.Q(**{field_name: ''})
            q_null = models.Q(**{field_name: None})
            return ~q & ~q_empty & ~q_null
        else:
            key = 'data__{}__{}'.format(field_name, operator)
            return models.Q(**{key: value})


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
