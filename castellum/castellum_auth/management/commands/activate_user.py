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
        default_date = timezone.now() + timezone.timedelta(days=7)
        parser.add_argument('date', type=parse_date, default=default_date, nargs='?')

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username=options['username'])
        if created:
            user.set_unusable_password()
        user.expiration_date = options['date']
        user.save()
