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


"""Filter queries for Subjects.

There are many complicated filters for Subjects.
In order to avoid losing track these are collected in this file.

All of the functions return instances of ``django.db.models.Q``,
which can be passed to ``Subjects.objects.filter()``.
"""

import json

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.db import models
from django.utils import timezone

from castellum.contacts.models import Contact
from castellum.studies.models import Study
from castellum.subjects.models import Subject

from .models import AttributeDescription
from .models import Participation


def _reverse_exclusive_studies():
    return models.Q(
        ~models.Q(study__status=Study.FINISHED),
        ~models.Q(status=Participation.UNSUITABLE),
        study__is_exclusive=True,
    )


def study_exclusion(study):
    """Handle the different kinds of exclusiveness between studies."""

    # Excluded studies
    pr_q = models.Q(
        study__in=study.excluded_studies.all(),
        status=Participation.INVITED,
    )

    # Reverse excluded studies:
    # Exclude studies which exclude this study.
    pr_q |= models.Q(
        study__excluded_studies=study,
        status=Participation.INVITED,
    )

    if study.is_exclusive:
        # Exclusive studies:
        # Exclude all other studies (including exclusive studies).
        pr_q |= models.Q(
            ~models.Q(study__status=Study.FINISHED),
            ~models.Q(status=Participation.UNSUITABLE),
            ~models.Q(study__pk=study.pk),
        )
    else:
        # Reverse exclusive studies:
        # All other studies still exclude exclusive studies.
        pr_q |= _reverse_exclusive_studies()

    prs = Participation._base_manager.filter(pr_q)

    return ~models.Q(pk__in=prs.values('subject'))


def study_disinterest(study):
    """Exclude subjects who are disinterested in this study's study type."""
    return ~models.Q(study_type_disinterest__in=study.study_type.all())


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

    q = models.Q(consent__document__isnull=False)

    if exclude_deprecated:
        q &= models.Q(consent__document__is_deprecated=False)

    if include_waiting:
        acceptable_datetime = timezone.now() - settings.CASTELLUM_CONSENT_REVIEW_PERIOD
        q |= models.Q(consent__isnull=True, created_at__gte=acceptable_datetime)

    return q & models.Q(deceased=False, blocked=False)


def to_be_deleted():
    """Exclude subjects who want to be deleted."""
    return models.Q(to_be_deleted__isnull=True)


def already_in_study(study):
    """Exclude subjects if they already have a participation in this study."""
    return ~models.Q(participation__study=study)


def study_filters(study, include_unknown=None):
    """A wrapper around subjectfilters()."""

    # Filter according to all subjectfilters from all
    # subjectfiltergroups.
    q = models.Q()
    for group in study.subjectfiltergroup_set.all():
        q |= subjectfilters(group, include_unknown=include_unknown)

    return q


def uuid_filter(qs, key='subject_uuid'):
    # This is a micro-optimization to avoid large IN queries in postgres
    # See https://dba.stackexchange.com/questions/91247
    uuids = set(qs.values_list(key, flat=True).order_by())
    total = Subject.objects.count()
    if len(uuids) > total / 2:
        all_uuids = Subject.objects.values_list('uuid', flat=True)
        uuids = set(all_uuids).difference(uuids)
        return ~models.Q(uuid__in=uuids)
    else:
        return models.Q(uuid__in=uuids)


def geofilter(study):
    from castellum.geofilters.models import Geolocation

    data = json.load(study.geo_filter)
    study.geo_filter.seek(0)
    if data['type'] == 'FeatureCollection':
        features = data['features']
    else:
        features = [data]

    q = models.Q()
    for feature in features:
        polygon = GEOSGeometry(json.dumps(feature['geometry']))

        outside = Geolocation.objects.exclude(point__within=polygon)
        wards = (
            Contact.objects
            .exclude(legal_representatives__geolocation=None)
            .exclude(legal_representatives__geolocation__in=outside)
        )
        q |= models.Q(geolocation__point__within=polygon) | models.Q(id__in=wards.values('id'))

    return uuid_filter(Contact.objects.filter(q))


def completeness_expr():
    """Expression that can be used to annotate a queryset."""
    # Needs to match ``Subject.get_completeness()``.
    total = 0
    completeness = models.Value(0, output_field=models.IntegerField())
    for description in AttributeDescription.objects.all():
        total += 1
        field_name = 'attributes__' + description.json_key
        completeness += models.Case(
            models.When((
                models.Q(**{field_name: ''})
                | models.Q(**{field_name: None})
                | models.Q(**{field_name + '__isnull': True})
            ), models.Value(0)),
            default=models.Value(1),
        )
    return completeness, total


def study_except_filters(study, include_unknown=None):
    q = models.Q()
    q &= study_exclusion(study)
    q &= study_disinterest(study)
    q &= to_be_deleted()
    q &= models.Q(deceased=False)
    q &= models.Q(blocked=False)
    if 'castellum.geofilters' in settings.INSTALLED_APPS and study.geo_filter:
        q &= geofilter(study)
    return q


def study(study, include_unknown=None):
    """Combine all filters related to ``study``."""
    return (
        study_filters(study, include_unknown=include_unknown)
        & study_except_filters(study, include_unknown=include_unknown)
    )
