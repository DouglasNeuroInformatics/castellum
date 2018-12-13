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

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.utils import timezone

from castellum.castellum_auth.models import User

USERS = {
    'Andreas': [],
    'Vera': ['Study coordinator'],
    'Arne': ['Subject manager'],
    'Emma': ['Recruiter'],
    'Edwin': ['Subject manager', 'Recruiter'],
}


class Command(BaseCommand):
    help = 'Create a set of predefined users as examples'

    def handle(self, *args, **options):
        expiration_date = timezone.now() + timezone.timedelta(days=1000)

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 'admin@example.com', '123', expiration_date=expiration_date)

        for name, groups in USERS.items():
            defaults = {'email': name + '@example.com', 'expiration_date': expiration_date}
            user, created = User.objects.get_or_create(username=name, defaults=defaults)
            if created:
                user.set_password('123')
                user.user_permissions.add(Permission.objects.get(codename='privacy_level_1'))
                user.groups.set(Group.objects.filter(name__in=groups))
                user.save()
