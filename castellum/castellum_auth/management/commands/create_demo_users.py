# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils import timezone

from castellum.castellum_auth.models import User

USERS = {
    'Andreas': [],
    'Jonas': ['Subject manager', 'Data protection officer'],
    'Sabine': ['Receptionist'],

    # first testing group
    'Vera': ['Study coordinator', 'Study approver'],
    'Arne': ['Subject manager'],

    # second testing group
    'Anna': ['Study coordinator'],
    'Max': ['Subject manager'],

    # third testing group
    'Claus': ['Study coordinator'],
    'Flora': ['Subject manager'],

    # fourth testing group
    'Hans': ['Study coordinator'],
    'Nina': ['Subject manager'],
}


class Command(BaseCommand):
    help = 'Create a set of predefined users as examples'

    def handle(self, *args, **options):
        if settings.PRODUCTION:
            raise CommandError(
                'Creating demo users in production environment is insecure.'
            )

        expiration_date = timezone.now() + relativedelta(days=1000)

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin',
                'admin@example.com',
                User.DEMO_PASSWORD,
                expiration_date=expiration_date,
            )

        last_name = 'Test'
        for first_name, groups in USERS.items():
            name = first_name.lower()
            defaults = {
                'first_name': first_name,
                'last_name': last_name,
                'email': f'{name}@example.com',
                'expiration_date': expiration_date,
            }
            user, created = User.objects.get_or_create(username=name, defaults=defaults)
            if created:
                user.set_password(User.DEMO_PASSWORD)
                user.user_permissions.add(
                    Permission.objects.get(codename='privacy_level_1')
                )
                user.groups.set(Group.objects.filter(name__in=groups))
                user.save()
