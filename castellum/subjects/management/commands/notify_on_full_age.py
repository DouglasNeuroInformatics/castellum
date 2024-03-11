# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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
from django.core.management.base import CommandError

from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.subjects.models import Consent
from castellum.subjects.models import Subject
from castellum.utils.mail import MailContext


def send(months, attr):
    today = datetime.date.today()

    full_age_contacts = Contact.objects.filter(
        date_of_birth__lte=(
            today - relativedelta(
                years=settings.CASTELLUM_FULL_AGE,
                months=months,
            )
        )
    )

    subjects = (
        Subject.objects
        .filter(filter_queries.uuid_filter(full_age_contacts))
        .filter(consent__underage_when_given=True)
        .exclude(consent__document=None)
        .filter(**{f'consent__{attr}': False})
    )

    reached = 0
    not_reached = 0

    with MailContext('recruitment') as ctx:
        for subject in subjects.all():
            success = ctx.send_separate_mails(
                settings.CASTELLUM_FULL_AGE_MAIL_SUBJECT,
                settings.CASTELLUM_FULL_AGE_MAIL_BODY,
                subject.contact.own_or_legal_representative_emails,
                recipients_string=subject.contact.email_recipients_string,
            )
            if success:
                reached += 1
                Consent.objects.filter(subject_id=subject.pk).update(**{attr: True})
            else:
                not_reached += 1

    return reached, not_reached


class Command(BaseCommand):
    help = 'Contact subjects who recently came off age to renew their consent'

    def handle(self, *args, **options):
        if not settings.CASTELLUM_FULL_AGE_MAIL_SUBJECT:
            raise CommandError('CASTELLUM_FULL_AGE_MAIL_SUBJECT not set')
        if not settings.CASTELLUM_FULL_AGE_MAIL_BODY:
            raise CommandError('CASTELLUM_FULL_AGE_MAIL_BODY not set')

        reached, not_reached = send(1, 'full_age_notified_1')
        if options['verbosity'] > 0:
            self.stdout.write(f'full age notification 1 reached: {reached}')
            self.stdout.write(f'full age notification 1 not reached: {not_reached}')

        reached, not_reached = send(21, 'full_age_notified_2')
        if options['verbosity'] > 0:
            self.stdout.write(f'full age notification 2 reached: {reached}')
            self.stdout.write(f'full age notification 2 not reached: {not_reached}')
