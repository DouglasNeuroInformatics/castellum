# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.urls import reverse

from castellum.studies.models import Study
from castellum.subjects.models import Subject

from ..models import Attribute


class SubjectFilterGroupManager(models.Manager):
    def clone(self, original_group):
        cloned_group = SubjectFilterGroup.objects.create(study=original_group.study)
        SubjectFilter.objects.bulk_create(
            self.clone_filters(original_group, cloned_group)
        )
        return cloned_group

    def clone_filters(self, original_group, cloned_group):
        for f in original_group.subjectfilter_set.all():
            yield SubjectFilter(
                group=cloned_group,
                attribute=f.attribute,
                operator=f.operator,
                value=f.value,
            )


class SubjectFilterGroup(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE)

    objects = SubjectFilterGroupManager()

    def get_absolute_url(self):
        return reverse('studies:filtergroup-update', args=[self.study.pk, self.pk])

    def get_potential_matches(self):
        from .. import filter_queries

        return Subject.objects.filter(
            filter_queries.study_recruitable(self.study, enable_filters=False),
            filter_queries.subjectfilters(self),
            filter_queries.already_in_study(self.study, include_recruitment=False),
        )


class SubjectFilter(models.Model):
    group = models.ForeignKey(SubjectFilterGroup, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    operator = models.CharField(max_length=64)
    value = models.JSONField(editable=True)

    def __str__(self):
        return self.attribute.field.get_filter_display(self.operator, self.value)

    def to_q(self, include_unknown=True):
        return self.attribute.field.filter_to_q(
            self.operator, self.value, include_unknown
        )
