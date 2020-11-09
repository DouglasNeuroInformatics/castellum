
# (c) 2018-2020
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
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

import json

from django.core.management.base import BaseCommand

from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models.attributes import ANSWER_DECLINED
from castellum.subjects.models import Subject

TYPES = {
    'IntegerField': 'integer',
    'BooleanField': 'boolean',
}
FORMATS = {
    'DateField': 'date',
    'AgeField': 'date',
}


class Command(BaseCommand):
    help = 'Export attributes for a single subject (along with the schema).'

    def add_arguments(self, parser):
        parser.add_argument('subject_id', type=int)

    def handle(self, **options):
        subject = Subject.objects.get(pk=options['subject_id'])

        output = {
            'data': {},
            'schema': {
                'type': 'object',
                'properties': {},
            },
        }

        for description in AttributeDescription.objects.all():
            key = description.label
            choices = list(description.attributechoice_set.all())

            value = subject.attributes.get(description.json_key)
            if value in [None, ANSWER_DECLINED]:
                pass
            elif choices:
                choice = description.attributechoice_set.get(pk=value)
                output['data'][key] = choice.label
            else:
                output['data'][key] = value

            output['schema']['properties'][key] = {k: v for k, v in [
                ('type', TYPES.get(description.field_type, 'string')),
                ('format', FORMATS.get(description.field_type)),
                ('enum', [c.label for c in choices]),
                ('description', description.help_text),
            ] if v}

        print(json.dumps(output, sort_keys=True, indent=4))
