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


"""Filter queries for Subjects.

There are many complicted filters for Subjects.
In order to avoid losing track these are collected in this file.

All of the functions return instances of ``django.db.models.Q``,
which can be passed to ``Subjects.objects.filter()``.
"""

import json

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.utils import timezone

from castellum.studies.models import Study
from castellum.subjects.models import Consent
from castellum.subjects.models import Subject

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

    return ~models.Q(id__in=prs.values('subject_id'))


def study_disinterest(study):
    """Exclude subjects who are disinterested in this study's study type."""
    return ~models.Q(attributeset__study_type_disinterest__in=study.study_type.all())


def subjectfilters(subjectfiltergroup, include_unknown=None):
    """Exclude subjects according to subjectfilters from a single subjectfiltergroup."""

    if include_unknown is None:
        include_unknown = not subjectfiltergroup.study.complete_matches_only

    q = models.Q()
    for f in subjectfiltergroup.subjectfilter_set.all():
        q &= f.to_q(include_unknown=include_unknown)

    return q


def has_consent(include_waiting=False, exclude_deprecated=False):
    """Exclude subjects who do not want to be contacted for recruitment."""

    q_status = models.Q(consent__status=Consent.CONFIRMED)
    if include_waiting:
        acceptable_datetime = timezone.now() - settings.CASTELLUM_CONSENT_REVIEW_PERIOD
        q_status |= models.Q(consent__updated_at__gte=acceptable_datetime)

    q_document = models.Q(consent__document__is_valid=True)
    if exclude_deprecated:
        q_document &= models.Q(consent__document__is_deprecated=False)

    return q_status & q_document


def to_be_deleted():
    """Exclude subjects who want to be deleted."""
    return models.Q(to_be_deleted__isnull=True)


def already_in_study(study):
    """Exclude subjects if they already have a participationrequest in this study."""
    return ~models.Q(participationrequest__study=study)


def study_filters(study, include_unknown=None):
    """A wrapper around subjectfilters()."""

    if study.custom_filter:
        q = custom_filters[study.custom_filter](include_unknown=include_unknown)
    else:
        # Filter according to all subjectfilters from all
        # subjectfiltergroups.
        q = models.Q()
        for group in study.subjectfiltergroup_set.all():
            q |= subjectfilters(group, include_unknown=include_unknown)

    return q


def pk_filter(qs, key='subject_id'):
    pks = list(qs.values_list(key, flat=True).order_by())
    return models.Q(pk__in=pks)


def geofilter(study, include_unknown=None):
    from castellum.geofilters.models import Geolocation

    if include_unknown is None:
        include_unknown = not study.complete_matches_only

    feature = json.load(study.geo_filter)
    study.geo_filter.seek(0)
    polygon = GEOSGeometry(json.dumps(feature['geometry']))

    if include_unknown:
        locations = Geolocation.objects.exclude(point__within=polygon)
        return ~pk_filter(locations, 'contact__subject_id')
    else:
        locations = Geolocation.objects.filter(point__within=polygon)
        return pk_filter(locations, 'contact__subject_id')


def completeness_expr():
    """Expression that can be used to annotate a queryset."""
    # Needs to match ``AttributeSet.get_completeness()``.
    total = 0
    completeness = models.Value(0, output_field=models.IntegerField())
    for description in AttributeDescription.objects.all():
        total += 1
        field_name = 'attributeset__data__' + description.json_key
        completeness += models.Case(
            models.When((
                models.Q(**{field_name: ''}) |
                models.Q(**{field_name: None}) |
                models.Q(**{field_name + '__isnull': True})
            ), models.Value(0)),
            default=models.Value(1),
        )
    return completeness, total


def study_except_filters(study, include_unknown=None):
    q = models.Q()
    q &= study_exclusion(study)
    q &= study_disinterest(study)
    q &= to_be_deleted()
    if 'castellum.geofilters' in settings.INSTALLED_APPS and study.geo_filter:
        q &= geofilter(study, include_unknown=include_unknown)
    return q


def study(study, include_unknown=None):
    """Combine all filters related to ``study``."""
    return (
        study_filters(study, include_unknown=include_unknown)
        & study_except_filters(study, include_unknown=include_unknown)
    )
