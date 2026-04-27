# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.management.base import BaseCommand

from castellum.recruitment.models import Attribute
from castellum.subjects.models import Subject


class Command(BaseCommand):
    help = 'Remove high-privacy-level attributes from low-privacy-level subjects.'

    # NOTE: This is not done on delete to avoid accidental data loss.

    def handle(self, *args, **options):
        for attr in Attribute.objects.filter(privacy_level__gt=0):
            subjects = Subject.objects.filter(
                privacy_level__lt=attr.privacy_level,
                attributes__has_key=attr.json_key,
            )

            updates = []
            for subject in subjects:
                subject.attributes.pop(attr.json_key, None)
                updates.append(subject)
            Subject.objects.bulk_update(updates, ['attributes'])

            if updates and options['verbosity'] > 0:
                self.stdout.write(f'Cleared {attr} from {len(updates)} subjects')
