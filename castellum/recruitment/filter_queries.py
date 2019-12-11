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


"""Filter queries for AttributeSets.

There are many complicted filters for AttributeSets.
In order to avoid losing track these are collected in this file.

All of the functions return instances of ``django.db.models.Q``,
which can be passed to ``AttributeSet.objects.filter()``.
"""


from django.db import models

from castellum.studies.models import Study

from .filter_registry import custom_filters
from .models import AttributeDescription
from .models import ParticipationRequest


def study_exclusion(study):
    """Handle the different kinds of exclusiveness between studies."""

    # Excluded studies
    pr_q = models.Q(
        study__in=study.excluded_studies.all(),
        status=ParticipationRequest.INVITED,
    )

    # Reverse excluded studies:
    # Exclude studies which exclude this study.
    pr_q |= models.Q(
        study__excluded_studies=study,
        status=ParticipationRequest.INVITED,
    )

    if study.is_exclusive:
        # Exclusive studies:
        # Exclude all other studies (including exclusive studies).
        pr_q |= models.Q(
            ~models.Q(study__status=Study.FINISHED),
            ~models.Q(status=ParticipationRequest.UNSUITABLE),
            ~models.Q(study__pk=study.pk),
        )
    else:
        # Reverse exclusive studies:
        # All other studies still exclude exclusive studies.
        pr_q |= models.Q(
            ~models.Q(study__status=Study.FINISHED),
            ~models.Q(status=ParticipationRequest.UNSUITABLE),
            study__is_exclusive=True,
        )

    prs = ParticipationRequest._base_manager.filter(pr_q)

    return ~models.Q(subject_id__in=prs.values('subject_id'))


def study_disinterest(study):
    """Exclude subjects who are disinterested in this study's study type."""
    return ~models.Q(study_type_disinterest__in=study.study_type.all())


def subjectfilters(subjectfiltergroup, include_unknown=True):
    """Exclude subjects according to subjectfilters from a single subjectfiltergroup."""
    q = models.Q()
    for f in subjectfiltergroup.subjectfilter_set.all():
        q &= f.to_q(include_unknown=include_unknown)

    return q


def no_recruitment(study):
    """Exclude subjects who do not want to be contacted for recruitment."""
    return models.Q(subject__no_recruitment=False)


def already_in_study(study):
    """Exclude subjects if they already have a participationrequest in this study."""
    return ~models.Q(subject__participationrequest__study=study)


def study_filters(study, include_unknown=None):
    """A wrapper around subjectfilters()."""

    if include_unknown is None:
        include_unknown = not study.complete_matches_only

    if study.custom_filter:
        q = custom_filters[study.custom_filter](include_unknown=include_unknown)
    else:
        # Filter according to all subjectfilters from all
        # subjectfiltergroups.
        q = models.Q()
        for group in study.subjectfiltergroup_set.all():
            q |= subjectfilters(group, include_unknown=include_unknown)

    return q


def complete():
    q = models.Q()
    for description in AttributeDescription.objects.all():
        field_name = 'data__' + description.json_key
        q &= ~models.Q(**{field_name: ''})
        q &= ~models.Q(**{field_name: None})
        q &= ~models.Q(**{field_name + '__isnull': True})
    return q


def study(study, include_unknown=None):
    """Combine all filters related to ``study``."""
    q = models.Q()
    q &= study_exclusion(study)
    q &= study_disinterest(study)
    q &= study_filters(study, include_unknown=include_unknown)
    return q
