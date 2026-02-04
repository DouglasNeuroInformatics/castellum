# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import uuid

from django.core.management.base import BaseCommand

from castellum.recruitment.attribute_exporters import get_exporter
from castellum.recruitment.models import Attribute
from castellum.subjects.models import Subject


class Command(BaseCommand):
    help = 'Export recruitment attributes for a single subject or the attribute schema.'

    def add_arguments(self, parser):
        parser.add_argument('subject_uuid', type=uuid.UUID, nargs='?')
        parser.add_argument('--exporter')

    def handle(self, **options):
        exporter = get_exporter(options.get('exporter'))
        attributes = Attribute.objects.all()
        if options['subject_uuid'] is None:
            s = exporter.get_schema(attributes)
        else:
            subject = Subject.objects.get(pk=options['subject_uuid'])
            s = exporter.get_data(attributes, [(subject.pk, subject)])
        self.stdout.write(s)
