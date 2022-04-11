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

from django.conf import settings
from django.db import models

from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.subjects.models import Subject
from castellum.utils.expressions import exists


def get_export_requested():
    return Subject.objects.filter(export_requested__isnull=False).annotate(
        due=models.ExpressionWrapper(
            models.F('export_requested') + settings.CASTELLUM_SUBJECT_DELETION_PERIOD,
            output_field=models.DateField(),
        )
    ).order_by('export_requested')


def get_no_legal_basis():
    # this query has the biggest potential to shrink down
    # the number of matches, so it is done first
    subjects = (
        Subject.objects
        .alias(pr_count=models.Count(
            'participation', filter=~models.Q(participation__status=Participation.UNSUITABLE)
        ))
        .exclude(pk__in=Subject.objects.filter(
            filter_queries.has_consent(include_waiting=True), deceased=False
        ))
        .exclude(blocked=True, deceased=False)
        .filter(pr_count=0)
    )
    subject_uuids = subjects.values_list('uuid', flat=True)

    contacts = (
        Contact.objects
        .alias(legal_representative_of_count=models.Count('legal_representative_of'))
        .filter(legal_representative_of_count=0, subject_uuid__in=list(subject_uuids))
    )

    return Subject.objects.filter(filter_queries.uuid_filter(contacts))


def get_unreachable():
    contacts = (
        Contact.objects
        .alias(legal_representative_count=models.Count('legal_representatives'))
        .filter(
            legal_representative_count=0,
            address=None,
            email='',
            phone_number='',
        )
        .order_by()
    )

    return Subject.objects.filter(filter_queries.uuid_filter(contacts))


def get_residual_recruitment_data():
    completeness, _total = filter_queries.completeness_expr()
    return (
        Subject.objects
        .alias(completeness=completeness)
        .exclude(filter_queries.has_consent(include_waiting=True))
        .filter(
            models.Q(completeness__gt=1 if settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID else 0)
            | ~models.Q(study_type_disinterest=None)
            | models.Q(anonymous_invitation_disinterest=True)
        )
    )


def get_participations_without_legal_basis():
    return (
        Participation.objects
        .filter(
            study__status=Study.FINISHED,
            study__domains=None,
        )
        .exclude(news_interest=Participation.NOT_INTERESTED)
    )


def get_should_delete_participations():
    return Subject.objects.filter(
        ~filter_queries.has_consent(include_waiting=True),
        uuid__in=get_participations_without_legal_basis().values('subject_uuid'),
    )


def get_subjects():
    return (
        Subject.objects
        .prefetch_related(models.Prefetch(
            'participation_set',
            queryset=get_participations_without_legal_basis(),
            to_attr='participations_without_legal_basis',
        ))
        .annotate(
            # depending on database backend, this is either a date or a datetime
            due=models.ExpressionWrapper(
                models.Case(
                    models.When(
                        (
                            models.Q(export_requested__lt=models.F('to_be_deleted'))
                            | models.Q(to_be_deleted__isnull=True)
                        ),
                        then=models.F('export_requested'),
                    ),
                    default=models.F('to_be_deleted'),
                ) + settings.CASTELLUM_SUBJECT_DELETION_PERIOD,
                output_field=models.DateField(),
            ),
            no_legal_basis=exists(get_no_legal_basis(), pk=models.OuterRef('pk')),
            unreachable=exists(get_unreachable(), pk=models.OuterRef('pk')),
            residual_recruitment_data=exists(
                get_residual_recruitment_data(), pk=models.OuterRef('pk')
            ),
            should_delete_participations=exists(
                get_should_delete_participations(), pk=models.OuterRef('pk')
            ),
        )
        .exclude(
            export_requested__isnull=True,
            to_be_deleted__isnull=True,
            no_legal_basis=False,
            unreachable=False,
            residual_recruitment_data=False,
            should_delete_participations=False,
        )
        .order_by(models.F('due').asc(nulls_last=True))
    )
