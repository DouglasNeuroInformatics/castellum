# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.commands.migrate import Command as MigrateCommand


class Command(BaseCommand):
    help = 'Update database schema of all databases.'

    def handle(self, *args, **kwargs):
        migrate = MigrateCommand()

        options = {
            'skip_checks': False,
            'app_label': None,
            'migration_name': None,
            'interactive': True,
            'fake': False,
            'fake_initial': False,
            'plan': False,
            'run_syncdb': False,
            'check_unapplied': False,
            'prune': False,
        }
        options.update(kwargs)

        for database in settings.DATABASES:
            options['database'] = database
            if options['verbosity'] >= 1:
                self.stdout.write(self.style.MIGRATE_HEADING('Database:'))
                self.stdout.write(f'  {database}')
            migrate.handle(*args, **options)
            if options['verbosity'] >= 1:
                self.stdout.write('')
