# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from castellum.studies.models import Study
from castellum.subjects.models import Subject

from ..models import AttributeDescription
from ..models import Participation


class SubjectFilterGroupManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(index=models.Window(
            expression=models.functions.RowNumber(),
            order_by=[models.F('id')],
            partition_by=models.F('study'),
        ))

    def clone(self, original_group):
        cloned_group = SubjectFilterGroup.objects.create(study=original_group.study)
        SubjectFilter.objects.bulk_create(self.clone_filters(original_group, cloned_group))
        return cloned_group

    def clone_filters(self, original_group, cloned_group):
        for f in original_group.subjectfilter_set.all():
            yield SubjectFilter(
                group=cloned_group, description=f.description, operator=f.operator, value=f.value
            )


class SubjectFilterGroup(models.Model):
    name = models.CharField(_('Name'), max_length=254, blank=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    min_subject_count = models.PositiveIntegerField(_('Required number of subjects'), default=0)

    objects = SubjectFilterGroupManager()

    def get_absolute_url(self):
        return reverse('studies:filtergroup-update', args=[self.study.pk, self.pk])

    def get_potential_matches(self):
        from .. import filter_queries

        return Subject.objects.filter(
            filter_queries.study_except_filters(self.study),
            filter_queries.subjectfilters(self),
            filter_queries.has_consent(),
        ).exclude(
            pk__in=self.study.participation_set.filter(
                status__in=[Participation.INVITED, Participation.UNSUITABLE]
            ).values('subject')
        )

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '{} {}'.format(gettext('Group'), self.index)


class SubjectFilter(models.Model):
    group = models.ForeignKey(SubjectFilterGroup, on_delete=models.CASCADE)
    description = models.ForeignKey(AttributeDescription, on_delete=models.CASCADE)
    operator = models.CharField(max_length=64)
    value = models.JSONField(editable=True)

    def __str__(self):
        return self.description.field.get_filter_display(self.operator, self.value)

    def to_q(self, include_unknown=True):
        return self.description.field.filter_to_q(self.operator, self.value, include_unknown)
