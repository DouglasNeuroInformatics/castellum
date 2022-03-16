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

import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils import timezone

from castellum.castellum_auth.models import User

USERS = {
    'Andreas': [],
    'Jonas': ['Principal subject manager', 'Data protection coordinator'],
    'Sabine': ['Receptionist'],

    # first testing group
    'Vera': ['Study coordinator', 'Study approver'],
    'Arne': ['Principal subject manager'],

    # second testing group
    'Anna': ['Study coordinator'],
    'Max': ['Principal subject manager'],

    # third testing group
    'Claus': ['Study coordinator'],
    'Flora': ['Principal subject manager'],

    # fourth testing group
    'Hans': ['Study coordinator'],
    'Nina': ['Principal subject manager'],
}


class Command(BaseCommand):
    help = 'Create a set of predefined users as examples'

    def handle(self, *args, **options):
        if settings.PRODUCTION:
            raise CommandError('Creating demo users in production environment is insecure.')

        expiration_date = timezone.now() + datetime.timedelta(days=1000)

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 'admin@example.com', User.DEMO_PASSWORD, expiration_date=expiration_date
            )

        last_name = 'Test'
        for first_name, groups in USERS.items():
            name = first_name.lower()
            defaults = {
                'first_name': first_name,
                'last_name': last_name,
                'email': name + '@example.com',
                'expiration_date': expiration_date,
                'privacy_level': 1,
            }
            user, created = User.objects.get_or_create(username=name, defaults=defaults)
            if created:
                user.set_password(User.DEMO_PASSWORD)
                user.groups.set(Group.objects.filter(name__in=groups))
                user.save()
