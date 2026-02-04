# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
