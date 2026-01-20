# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from castellum.data_protection import helpers


def _delete(qs, created_before=None, dry_run=False):
    if created_before:
        qs = qs.filter(created_at__lt=created_before)
    if dry_run:
        return qs.count()
    else:
        return qs.delete()[0]


def delete_to_be_deleted(**kwargs):
    qs = helpers.get_subjects().filter(to_be_deleted__isnull=False)
    return _delete(qs, **kwargs)


def delete_no_legal_basis(**kwargs):
    qs = helpers.get_subjects().filter(no_legal_basis=True)
    return _delete(qs, **kwargs)


def delete_unreachable(**kwargs):
    qs = helpers.get_subjects().filter(unreachable=True)
    return _delete(qs, **kwargs)


class Command(BaseCommand):
    help = 'Automatically clear dashboards by deleting subjects.'

    def add_arguments(self, parser):
        parser.add_argument('--to-be-deleted', action='store_true')
        parser.add_argument('--no-legal-basis', action='store_true')
        parser.add_argument('--unreachable', action='store_true')
        parser.add_argument('-m', '--created-before-months', type=int)
        parser.add_argument('-n', '--dry-run', action='store_true')

    def handle(self, *args, **options):
        kwargs = {'dry_run': options['dry_run']}
        if options['created_before_months']:
            kwargs['created_before'] = datetime.date.today() - relativedelta(
                months=options['created_before_months']
            )

        if options['to_be_deleted']:
            deleted = delete_to_be_deleted(**kwargs)
            if options['verbosity'] > 0:
                self.stdout.write(
                    f'Automatically deleted {deleted} subjects marked for deletion'
                )

        if options['no_legal_basis']:
            deleted = delete_no_legal_basis(**kwargs)
            if options['verbosity'] > 0:
                self.stdout.write(
                    f'Automatically deleted {deleted} subjects without legal basis'
                )

        if options['unreachable']:
            deleted = delete_unreachable(**kwargs)
            if options['verbosity'] > 0:
                self.stdout.write(
                    f'Automatically deleted {deleted} unreachable subjects'
                )
