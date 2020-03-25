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

import datetime

from django.core.management.base import BaseCommand

from dateutil.relativedelta import relativedelta

from castellum.contacts.models import Contact
from castellum.subjects.models import Subject

FULL_AGE = relativedelta(years=18)


class Command(BaseCommand):
    help = "Invalidate recruitment consent for all children that come of age."

    def handle(self, *args, **kwargs):
        today = datetime.date.today()

        # date_of_birth is stored in Contact, so we cannot query it
        # directly. As an optimization, we only look at subjects that
        # came of age in the past year.
        contacts = Contact.objects.filter(
            date_of_birth__lt=today - FULL_AGE,
            date_of_birth__gt=today - FULL_AGE - relativedelta(years=1),
        ).values_list('subject_id', flat=True)

        subjects = Subject.objects.filter(
            consent__document__is_current=True,
            pk__in=list(contacts),
        )

        for subject in subjects:
            if subject.consent.updated_at.date() < subject.contact.date_of_birth + FULL_AGE:
                subject.consent.delete()
