# (c) 2018-2021
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

from django.conf import settings
from django.db import models

from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.subjects.models import Subject


def get_export_requested(limit_by):
    subjects = Subject.objects.filter(export_requested__isnull=False).annotate(
        due=models.ExpressionWrapper(
            models.F('export_requested') + settings.CASTELLUM_SUBJECT_DELETION_PERIOD,
            output_field=models.DateField(),
        )
    ).order_by('export_requested')

    return subjects[:limit_by], max(subjects.count() - limit_by, 0)


def get_to_be_deleted(limit_by):
    subjects = Subject.objects.filter(to_be_deleted__isnull=False).annotate(
        due=models.ExpressionWrapper(
            models.F('to_be_deleted') + settings.CASTELLUM_SUBJECT_DELETION_PERIOD,
            output_field=models.DateField(),
        )
    ).order_by('to_be_deleted')

    return subjects[:limit_by], max(subjects.count() - limit_by, 0)


def get_no_legal_basis(limit_by):
    # this query has the biggest potential to shrink down
    # the number of matches, so it is done first
    subjects = Subject.objects\
        .annotate(pr_count=models.Count('participation', filter=~models.Q(
            participation__status=Participation.UNSUITABLE
        )))\
        .exclude(filter_queries.has_consent(include_waiting=True), deceased=False)\
        .filter(pr_count=0)
    subject_pks = subjects.values_list('pk', flat=True)

    contacts = Contact.objects\
        .annotate(guardian_of_count=models.Count('guardian_of'))\
        .filter(guardian_of_count=0, subject_id__in=list(subject_pks))

    subjects = Subject.objects.filter(filter_queries.pk_filter(contacts))

    return subjects[:limit_by], max(subjects.count() - limit_by, 0)


def get_unreachable(limit_by):
    contacts = Contact.objects\
        .annotate(guardian_count=models.Count('guardians'))\
        .filter(
            guardian_count=0,
            address=None,
            email='',
            phone_number='',
        )\
        .order_by()

    subjects = Subject.objects.filter(filter_queries.pk_filter(contacts))

    return subjects[:limit_by], max(subjects.count() - limit_by, 0)


def get_all_subjects(limit_by):
    subjects = set()
    missing = 0
    for fn in [get_to_be_deleted, get_no_legal_basis, get_unreachable]:
        s, m = fn(limit_by)
        subjects.update(s)
        missing += m
    return subjects, missing
