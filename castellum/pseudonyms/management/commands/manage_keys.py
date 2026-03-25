# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.management.base import BaseCommand

from castellum.pseudonyms.models import KeyPair
from castellum.pseudonyms.models import Pseudonym


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('action', choices=['public', 'private', 'delete'])
        parser.add_argument('domain')
        parser.add_argument('pseudonym')

    def handle(self, action, domain, pseudonym, **options):
        p = Pseudonym.objects.get(pseudonym=pseudonym, domain__key=domain)
        key_pair, _ = KeyPair.objects.get_or_create(pseudonym=p)
        if action == 'delete':
            key_pair.delete()
        elif action == 'private':
            self.stdout.write(key_pair.get_ssh_private_key())
        else:
            self.stdout.write(key_pair.get_ssh_public_key())

