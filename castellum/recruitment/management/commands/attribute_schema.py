
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

TYPES = {
    'IntegerField': 'integer',
    'BooleanField': 'boolean',
}
FORMATS = {
    'DateField': 'date',
    'AgeField': 'date',
}


class Command(BaseCommand):
    help = 'Export current attribute schema as JSONSchema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--raw', action='store_true', help='create schema as actually used in the database'
        )

    def handle(self, **options):
        schema = {
            'type': 'object',
            'properties': {},
        }
        for description in AttributeDescription.objects.all():
            choices = list(description.attributechoice_set.all())
            if options['raw']:
                key = description.json_key
                fields = [
                    ('type', TYPES.get(description.field_type, 'integer' if choices else 'string')),
                    ('format', FORMATS.get(description.field_type)),
                    ('enum', [c.pk for c in choices]),
                    ('description', description.label),
                ]
            else:
                key = description.label
                fields = [
                    ('type', TYPES.get(description.field_type, 'string')),
                    ('format', FORMATS.get(description.field_type)),
                    ('enum', [c.label for c in choices]),
                    ('description', description.help_text),
                ]
            schema['properties'][key] = {k: v for k, v in fields if v}
        print(json.dumps(schema, sort_keys=True, indent=4))
