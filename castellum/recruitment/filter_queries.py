# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later


"""Filter queries for Subjects.

There are many complicated filters for Subjects.
In order to avoid losing track these are collected in this file.

All of the functions return instances of ``django.db.models.Q``,
which can be passed to ``Subjects.objects.filter()``.
"""

import datetime
import json

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.db.models.functions import Greatest
from django.utils import timezone

from castellum.contacts.models import Contact
from castellum.studies.models import Study
from castellum.subjects.models import Subject
from castellum.utils.models import value_set

from .models import Attribute
from .models import Participation


def _reverse_exclusive_studies():
    return models.Q(
        ~models.Q(study__status=Study.FINISHED),
        ~models.Q(status__in=[
            *Participation.EXCLUDED_SET,
            Participation.PARTICIPATING_DROPPED_OUT,
            Participation.COMPLETED,
        ]),
        study__is_exclusive=True,
    )


def study_exclusion(study):
    """Handle the different kinds of exclusiveness between studies."""

    # Excluded studies
    pr_q = models.Q(
        study__in=study.excluded_studies.all(),
        status__in=[
            *Participation.INVITED_SET,
            Participation.EXCLUDED_DROPPED_OUT,
        ],
    )

    # Reverse excluded studies:
    # Exclude studies which exclude this study.
    pr_q |= models.Q(
        study__excluded_studies=study,
        status__in=[
            *Participation.INVITED_SET,
            Participation.EXCLUDED_DROPPED_OUT,
        ],
    )

    if study.is_exclusive:
        # Exclusive studies:
        # Exclude all other studies (including exclusive studies).
        pr_q |= models.Q(
            ~models.Q(study__status=Study.FINISHED),
            ~models.Q(status__in=[
                *Participation.EXCLUDED_SET,
                Participation.PARTICIPATING_DROPPED_OUT,
                Participation.COMPLETED,
            ]),
            ~models.Q(study__pk=study.pk),
        )
    else:
        # Reverse exclusive studies:
        # All other studies still exclude exclusive studies.
        pr_q |= _reverse_exclusive_studies()

    prs = Participation.objects.filter(pr_q)

    q = ~models.Q(pk__in=prs.values('subject'))

    # Included studies
    if study.included_studies.exists():
        q &= models.Q(pk__in=Participation.objects.filter(
            status__in=[
                Participation.PARTICIPATING,
                Participation.COMPLETED,
            ],
            study__in=study.included_studies.all(),
        ).values('subject'))

    return q


def study_disinterest(study):
    """Exclude subjects who are disinterested in this study's study type."""
    return ~models.Q(study_type_disinterest__in=study.study_type.all())


def study_max_privacy_level(study):
    """Exclude subjects who no study members can access."""
    return models.Q(privacy_level__lte=study.members_max_privacy_level)


def last_study_participation(before=None, after=None):
    """Exclude subjects based on last study activity.

    -   The goal is to only include activity that has actually happend
    -   If appointments are not available, look at completed participations
    -   If those are also not available, use ``Subject.created_at``

    Last study participation is distinct from last contact (``Subject.updated_at``).
    """

    if not before and not after:
        return models.Q()

    today = datetime.date.today()

    qs = Subject.objects.alias(
        last_appointment=models.Max('participation__appointment__start__date', filter=(
            models.Q(participation__appointment__start__date__lt=today)
        )),
        last_participation=models.Max('participation__updated_at__date', filter=(
            models.Q(participation__status=Participation.COMPLETED) | models.Q(
                participation__status__in=Participation.INVITED_SET,
                participation__study__status=Study.FINISHED,
            )
        )),
    ).alias(
        last_active=Greatest(
            Coalesce('last_appointment', 'created_at'),
            Coalesce('last_participation', 'created_at'),
        )
    )

    if before:
        qs = qs.filter(last_active__lte=before)
    if after:
        qs = qs.filter(last_active__gte=after)

    return models.Q(pk__in=qs)


def subjectfilters(subjectfiltergroup, include_unknown=None):
    """Exclude subjects according to subjectfilters from a single subjectfiltergroup."""

    if include_unknown is None:
        include_unknown = not subjectfiltergroup.study.complete_matches_only

    q = models.Q()
    for f in subjectfiltergroup.subjectfilter_set.all():
        q &= f.to_q(include_unknown=include_unknown)

    return q


def to_be_deleted():
    """Exclude subjects who want to be deleted."""
    return models.Q(to_be_deleted__isnull=True)


def is_available():
    return (
        models.Q(not_available_until=None)
        | models.Q(not_available_until__lte=timezone.localtime())
    )


def has_consent(
    include_waiting=False,
    exclude_deprecated=False,
    include_ineffective=False,
):
    """Exclude subjects who do not want to be contacted for recruitment."""

    q = models.Q(consent__document__is_valid=True)

    if exclude_deprecated:
        q &= models.Q(consent__document__is_deprecated=False)

    if include_waiting:
        acceptable_date = (
            datetime.date.today() - settings.CASTELLUM_CONSENT_REVIEW_PERIOD
        )
        q |= models.Q(consent__isnull=True, created_at__gte=acceptable_date)

    if not include_ineffective:
        q &= models.Q(deceased=False, blocked=False)
        q &= to_be_deleted()

    return q


def already_in_study(study, *, include_recruitment=True):
    """Exclude subjects if they already have a participation in this study."""
    if include_recruitment:
        return ~models.Q(participation__study=study)
    else:
        return ~models.Q(
            pk__in=study.participation_set.exclude(
                status__in=Participation.RECRUITMENT_SET
            ).values('subject')
        )


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
    uuids = value_set(qs, key)
    total = Subject.objects.count()
    if len(uuids) > total / 2:
        uuids = value_set(Subject.objects.all(), 'uuid').difference(uuids)
        return ~models.Q(uuid__in=uuids)
    else:
        return models.Q(uuid__in=uuids)


def geofilter(study):
    from django.contrib.gis.geos import GEOSGeometry

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
        q |= models.Q(geolocation__point__within=polygon)

        outside = Geolocation.objects.exclude(point__within=polygon)
        wards = (
            Contact.objects
            .exclude(legal_representatives__geolocation=None)
            .exclude(legal_representatives__geolocation__in=outside)
        )
        q |= models.Q(id__in=wards.values('id'))

    return uuid_filter(Contact.objects.filter(q))


def reliability(study):
    if study.max_reliability_issues is None:
        return models.Q()

    return models.Q(pk__in=(
        Subject.objects
        .annotate_reliability()
        .filter(reliability_issues__lte=study.max_reliability_issues)
        .order_by()
    ))


def completeness_expr(exclude_auto_fields=False):
    """Expression that can be used to annotate a queryset."""
    # Needs to match ``Subject.get_completeness()``.
    total = 0
    completeness = models.Value(0, output_field=models.IntegerField())
    attrs = Attribute.objects.all()
    if exclude_auto_fields:
        attrs = attrs.exclude(pk=settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID)
    for attribute in attrs:
        total += 1
        field_name = f'attributes__{attribute.json_key}'
        completeness += models.Case(
            models.When((
                models.Q(**{field_name: ''})
                | models.Q(**{field_name: None})
                | models.Q(**{f'{field_name}__isnull': True})
            ), models.Value(0)),
            default=models.Value(1),
        )
    return completeness, total


def study_criteria(study, *, enable_filters=True, include_unknown=None):
    q = models.Q()
    q &= study_exclusion(study)
    q &= study_disinterest(study)
    if 'castellum.geofilters' in settings.INSTALLED_APPS and study.geo_filter:
        q &= geofilter(study)
    if enable_filters:
        q &= study_filters(study, include_unknown=include_unknown)
    return q


def study_recruitable(study, **kwargs):
    return (
        study_criteria(study, **kwargs)
        & has_consent()
        & is_available()
        & study_max_privacy_level(study)
        & reliability(study)
        & last_study_participation(
            before=study.recruitment_active_before,
            after=study.recruitment_active_after,
        )
    )
