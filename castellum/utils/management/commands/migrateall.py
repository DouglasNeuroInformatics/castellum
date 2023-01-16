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

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.commands.migrate import Command as MigrateCommand


class Command(BaseCommand):
    help = "Update database schema of all databases."

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
        }
        options.update(kwargs)

        for database in settings.DATABASES:
            options['database'] = database
            if options['verbosity'] >= 1:
                self.stdout.write(self.style.MIGRATE_HEADING("Database:"))
                self.stdout.write('  ' + database)
            migrate.handle(*args, **options)
            if options['verbosity'] >= 1:
                self.stdout.write('')
