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

from castellum.studies.models import Study

from .filter_registry import custom_filters
from .models import ParticipationRequest


def study_exclusion(study):
    q = ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
        study__in=study.excluded_studies.all(),
        status=ParticipationRequest.INVITED,
    ).values('subject_id'))

    q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
        study__excluded_studies=study,
        status=ParticipationRequest.INVITED,
    ).values('subject_id'))

    if study.is_exclusive:
        q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
            ~models.Q(study__status=Study.FINISHED),
            ~models.Q(status=ParticipationRequest.UNSUITABLE),
            ~models.Q(study__pk=study.pk),
        ).values('subject_id'))

    else:
        q &= ~models.Q(subject_id__in=ParticipationRequest._base_manager.filter(
            ~models.Q(study__status=Study.FINISHED),
            ~models.Q(status=ParticipationRequest.UNSUITABLE),
            study__is_exclusive=True,
        ).values('subject_id'))

    return q


def study_disinterest(study):
    return ~models.Q(study_type_disinterest__in=study.study_type.all())


def subjectfilters(subjectfiltergroup, include_unknown=True):
    q = models.Q()
    for f in subjectfiltergroup.subjectfilter_set.all():
        q &= f.to_q(include_unknown=include_unknown)

    return q


def no_recruitment(study):
    return models.Q(subject__no_recruitment=False)


def already_in_study(study):
    return ~models.Q(subject__participationrequest__study=study)


def study_filters(study, include_unknown=None):
    if include_unknown is None:
        include_unknown = not study.complete_matches_only

    if study.custom_filter:
        q = custom_filters[study.custom_filter](include_unknown=include_unknown)
    else:
        q = models.Q()
        for group in study.subjectfiltergroup_set.all():
            q |= subjectfilters(group, include_unknown=include_unknown)

    return q


def study(study, include_unknown=None):
    q = models.Q()
    q &= study_exclusion(study)
    q &= study_disinterest(study)
    q &= study_filters(study, include_unknown=include_unknown)
    return q
