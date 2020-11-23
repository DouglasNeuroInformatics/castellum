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

from .attribute_fields import ANSWER_DECLINED


class JSONExporter:
    TYPES = {
        'IntegerField': 'integer',
        'BooleanField': 'boolean',
    }
    FORMATS = {
        'DateField': 'date',
        'AgeField': 'date',
    }

    def get_schema(self, descriptions):
        schema = {
            'type': 'object',
            'properties': {},
        }

        for description in descriptions:
            key = description.label
            choices = list(description.attributechoice_set.all())

            schema['properties'][key] = {k: v for k, v in [
                ('type', self.TYPES.get(description.field_type, 'string')),
                ('format', self.FORMATS.get(description.field_type)),
                ('enum', [c.label for c in choices]),
                ('description', description.help_text),
            ] if v}

        return json.dumps(schema, sort_keys=True, indent=4)

    def get_data(self, descriptions, subjects):
        data = []

        for subject in subjects:
            data.append({})

            for description in descriptions:
                key = description.label
                choices = list(description.attributechoice_set.all())

                value = subject.attributes.get(description.json_key)
                if value in [None, ANSWER_DECLINED]:
                    pass
                elif choices:
                    choice = description.attributechoice_set.get(pk=value)
                    data[-1][key] = choice.label
                else:
                    data[-1][key] = value

        return json.dumps(data, sort_keys=True, indent=4)
