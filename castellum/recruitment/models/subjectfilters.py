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

from picklefield.fields import PickledObjectField

from castellum.studies.models import Study

from ..models import AttributeDescription
from ..models import AttributeSet
from ..models import ParticipationRequest


class SubjectFilterGroupManager(models.Manager):
    def clone(self, original_group):
        cloned_group = SubjectFilterGroup.objects.create(study=original_group.study)
        SubjectFilter.objects.bulk_create(self.clone_filters(original_group, cloned_group))
        return cloned_group

    def clone_filters(self, original_group, cloned_group):
        for f in original_group.subjectfilter_set.all():
            yield SubjectFilter(group=cloned_group, description=f.description, operator=f.operator,
                                value=f.value)


class SubjectFilterGroup(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)

    objects = SubjectFilterGroupManager()

    def get_absolute_url(self):
        return reverse('studies:filtergroup-update', args=[self.study.pk, self.pk])

    def to_q_study_exclusion(self):
        q = ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
            study__in=self.study.excluded_studies.all(),
            status=ParticipationRequest.INVITED,
        ).values('subject_id'))

        q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
            study__excluded_studies=self.study,
            status=ParticipationRequest.INVITED,
        ).values('subject_id'))

        if self.study.is_exclusive:
            q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
                ~models.Q(study__status=Study.FINISHED),
                ~models.Q(status=ParticipationRequest.UNSUITABLE),
                ~models.Q(study__pk=self.study.pk),
            ).values('subject_id'))

        else:
            q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
                ~models.Q(study__status=Study.FINISHED),
                ~models.Q(status=ParticipationRequest.UNSUITABLE),
                study__is_exclusive=True,
            ).values('subject_id'))

        return q

    def to_q_study_disinterest(self):
        return ~models.Q(study_type_disinterest__in=self.study.study_type.all())

    def to_q(self, include_unknown=True):
        for f in self.subjectfilter_set.all():
            q &= f.to_q(include_unknown=include_unknown)
        return q

    def get_matches(self):
        return AttributeSet.objects.filter(
            self.to_q(),
            self.to_q_study_exclusion(),
            self.to_q_study_disinterest(),
        )


class SubjectFilter(models.Model):
    group = models.ForeignKey(SubjectFilterGroup, on_delete=models.CASCADE)
    description = models.ForeignKey(AttributeDescription, on_delete=models.CASCADE)
    operator = models.CharField(max_length=64)
    value = PickledObjectField(editable=True)

    def __str__(self):
        return self.description.field.get_filter_display(self.operator, self.value)

    def to_q(self, include_unknown=True):
        return self.description.field.filter_to_q(self.operator, self.value, include_unknown)
