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

import re

from django.core.management.base import BaseCommand

from castellum.contacts.models import Street

RE_STREET = re.compile(r'    <tag k="addr:street" v="(.*)"/>')


def get_streets(path):
    names = set()
    with open(path) as fh:
        for line in fh:
            m = RE_STREET.match(line)
            if m:
                names.add(m.group(1))
    return sorted(names)


class Command(BaseCommand):
    help = 'Import street names from OSM (XML) data.'

    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument(
            '-c',
            '--clear',
            action='store_true',
            help='Clear existing streets before adding new ones',
        )

    def handle(self, **options):
        streets = get_streets(options['path'])
        if options['clear']:
            Street.objects.all().delete()
        Street.objects.bulk_create(Street(name=name) for name in streets)
        if options['verbosity'] > 0:
            self.stdout.write(f'Created {len(streets)} streets')
