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

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from picklefield.fields import PickledObjectField

from castellum.studies.models import Study

from ..models import AttributeDescription
from ..models import AttributeSet
from ..models import ParticipationRequest


class SubjectFilterGroupManager(models.Manager):
    def clone(self, original_group):
        cloned_group = SubjectFilterGroup.objects.create(study=original_group.study)
        SubjectFilter.objects.bulk_create(self.clone_filters(original_group, cloned_group))
        cloned_group.excluded_studies.add(*original_group.excluded_studies.all())
        return cloned_group

    def clone_filters(self, original_group, cloned_group):
        for f in original_group.subjectfilter_set.all():
            yield SubjectFilter(group=cloned_group, description=f.description, operator=f.operator,
                                value=f.value)


class SubjectFilterGroup(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    excluded_studies = models.ManyToManyField(
        Study, verbose_name=_('Excluded studies'), related_name='+', blank=True,
    )

    objects = SubjectFilterGroupManager()

    def get_absolute_url(self):
        return reverse('studies:filtergroup_update', args=[self.study.pk, self.pk])

    def to_q(self, include_unknown=True):
        q = ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
            study__in=self.excluded_studies.all(),
            status=ParticipationRequest.INVITED,
        ).values('subject_id'))

        if self.study.is_exclusive:
            q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
                ~models.Q(study__study_mode=Study.FINISHED),
                ~models.Q(status=ParticipationRequest.UNSUITABLE),
            ).values('subject_id'))

        else:
            q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
                ~models.Q(study__study_mode=Study.FINISHED),
                ~models.Q(status=ParticipationRequest.UNSUITABLE),
                study__is_exclusive=True,
            ).values('subject_id'))

        for f in self.subjectfilter_set.all():
            q &= f.to_q(include_unknown=include_unknown)

        return q

    def get_subject_count(self):
        return AttributeSet.objects.filter(self.to_q()).count()


class SubjectFilter(models.Model):
    group = models.ForeignKey(SubjectFilterGroup, on_delete=models.CASCADE)
    description = models.ForeignKey(AttributeDescription, on_delete=models.CASCADE)
    operator = models.CharField(max_length=64)
    value = PickledObjectField(editable=True)

    def __str__(self):
        return self.description.field.get_filter_display(self.operator, self.value)

    def to_q(self, include_unknown=True):
        return self.description.field.filter_to_q(self.operator, self.value, include_unknown)

    def get_subject_count(self, include_unknown=True):
        return AttributeSet.objects.filter(self.to_q(include_unknown)).count()
