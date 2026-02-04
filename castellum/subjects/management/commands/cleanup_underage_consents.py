# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
            date_of_birth__lt=(
                today - relativedelta(years=settings.CASTELLUM_FULL_AGE + 2)
            )
        )
        full_age_subjects = Subject.objects.filter(
            filter_queries.uuid_filter(full_age_contacts),
        )
        consents = Consent.objects.filter(
            underage_when_given=True,
            subject__in=full_age_subjects,
        ).exclude(document=None)

        count, _ = consents.delete()

        if options['verbosity'] > 0:
            self.stdout.write(f'Cleared {count} consents')
