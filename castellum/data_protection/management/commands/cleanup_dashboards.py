# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
