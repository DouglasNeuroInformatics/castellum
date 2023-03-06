# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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

import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management.base import BaseCommand

from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.subjects.models import Consent
from castellum.subjects.models import Subject


class Command(BaseCommand):
    help = 'Remove recruitment consents that were given before the subject came of age'

    def handle(self, *args, **options):
        today = datetime.date.today()

        full_age_contacts = Contact.objects.filter(
            date_of_birth__lt=today - relativedelta(years=settings.CASTELLUM_FULL_AGE + 2),
        )
        full_age_subjects = Subject.objects.filter(
            filter_queries.uuid_filter(full_age_contacts),
        )
        consents = Consent.objects.filter(
            underage_when_given=True,
            subject__in=full_age_subjects,
        )

        count, _ = consents.delete()

        if options['verbosity'] > 0 and count > 0:
            self.stdout.write(f'Cleared {count} consents')
