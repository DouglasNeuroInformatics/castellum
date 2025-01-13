# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from castellum.castellum_auth.models import User


def parse_date(s):
    dt = timezone.datetime.strptime(s, '%Y-%m-%d')
    return timezone.make_aware(dt)


class Command(BaseCommand):
    help = """Set the expiration date for a user.

    Create the user with an unusable password if it does not exist yet.
    """

    def add_arguments(self, parser):
        parser.add_argument('username')
        default_date = timezone.now() + relativedelta(weeks=1)
        parser.add_argument('date', type=parse_date, default=default_date, nargs='?')

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username=options['username'])
        if created:
            user.set_unusable_password()
        user.expiration_date = options['date']
        user.save()
