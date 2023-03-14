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

from castellum.data_protection import helpers


def delete_to_be_deleted():
    return helpers.get_subjects().filter(to_be_deleted__isnull=False).delete()[0]


def delete_no_legal_basis():
    return helpers.get_subjects().filter(no_legal_basis=True).delete()[0]


def delete_unreachable():
    return helpers.get_subjects().filter(unreachable=True).delete()[0]


class Command(BaseCommand):
    help = 'Automatically clear dashboards by deleting subjects.'

    def add_arguments(self, parser):
        parser.add_argument('--to_be_deleted', action='store_true')
        parser.add_argument('--no_legal_basis', action='store_true')
        parser.add_argument('--unreachable', action='store_true')

    def handle(self, *args, **options):
        if options['to_be_deleted']:
            deleted = delete_to_be_deleted()
            if options['verbosity'] > 0:
                self.stdout.write(
                    f'Automatically deleted {deleted} subjects marked for deletion'
                )

        if options['no_legal_basis']:
            deleted = delete_no_legal_basis()
            if options['verbosity'] > 0:
                self.stdout.write(
                    f'Automatically deleted {deleted} subjects without legal basis'
                )

        if options['unreachable']:
            deleted = delete_unreachable()
            if options['verbosity'] > 0:
                self.stdout.write(
                    f'Automatically deleted {deleted} unreachable subjects'
                )
