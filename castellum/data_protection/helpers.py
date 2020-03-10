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

from django.conf import settings
from django.db import models
from django.utils import timezone

from castellum.contacts.models import Contact
from castellum.recruitment.models import ParticipationRequest
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument
from castellum.subjects.models import Subject


def get_export_requested(limit_by):
    subjects = Subject.objects.filter(export_requested__isnull=False).annotate(
        due=models.ExpressionWrapper(
            models.F('export_requested') + settings.CASTELLUM_SUBJECT_DELETION_PERIOD,
            output_field=models.DateField(),
        )
    )

    return subjects[:limit_by], max(subjects.count() - limit_by, 0)


def get_to_be_deleted(limit_by):
    subjects = Subject.objects.filter(to_be_deleted__isnull=False).annotate(
        due=models.ExpressionWrapper(
            models.F('to_be_deleted') + settings.CASTELLUM_SUBJECT_DELETION_PERIOD,
            output_field=models.DateField(),
        )
    )

    return subjects[:limit_by], max(subjects.count() - limit_by, 0)


def get_orphans(limit_by):
    candidates = Subject.objects\
        .annotate(pr_count=models.Count('participationrequest', filter=~models.Q(
            participationrequest__status=ParticipationRequest.UNSUITABLE
        )))\
        .filter(no_recruitment=True, pr_count=0)

    subjects = []
    for subject in candidates:
        if len(subjects) >= limit_by:
            break
        if not subject.contact.guardian_of.exists():
            subjects.append(subject)

    # no way to efficiently determine missing
    return subjects, 0


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
    subjects = []
    for contact in contacts[:limit_by]:
        subjects.append(contact.subject)

    return subjects, max(contacts.count() - limit_by, 0)


def get_no_consent(limit_by):
    if not ConsentDocument.objects.exists():
        return [], 0

    acceptable_datetime = timezone.now() - settings.CASTELLUM_CONSENT_REVIEW_PERIOD
    subjects = Subject.objects.exclude(
        (
            models.Q(consent__status=Consent.CONFIRMED) |
            models.Q(consent__updated_at__lte=acceptable_datetime)
        ),
        consent__document__is_current=True,
    )

    return subjects[:limit_by], max(subjects.count() - limit_by, 0)


def get_all_subjects(limit_by):
    subjects = set()
    missing = 0
    for fn in [get_to_be_deleted, get_orphans, get_unreachable, get_no_consent]:
        s, m = fn(limit_by)
        subjects.update(s)
        missing += m
    return subjects, missing
