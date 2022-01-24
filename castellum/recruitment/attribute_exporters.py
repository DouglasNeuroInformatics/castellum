# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
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

import csv
import json
from io import StringIO

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.module_loading import import_string

from .attribute_fields import ANSWER_DECLINED


def get_exporter(path=None):
    cls = import_string(path or settings.CASTELLUM_ATTRIBUTE_EXPORTER)
    return cls()


class JSONExporter:
    TYPES = {
        'IntegerField': 'integer',
        'BooleanField': 'boolean',
        'MultipleChoiceField': 'array',
    }
    FORMATS = {
        'DateField': 'date',
        'AgeField': 'date',
    }

    def _json_dumps(self, data):
        return json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder)

    def get_schema(self, descriptions):
        schema = {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'string',
                },
            },
        }

        for description in descriptions:
            key = description.label
            choices = list(description.attributechoice_set.all())

            data = {k: v for k, v in [
                ('type', self.TYPES.get(description.field_type, 'string')),
                ('format', self.FORMATS.get(description.field_type)),
                ('enum', [c.label for c in choices]),
                ('description', description.help_text),
            ] if v}

            if data['type'] == 'array':
                enum = data.pop('enum')
                data['items'] = {
                    'type': 'string',
                    'enum': enum,
                }

            schema['properties'][key] = data

        return self._json_dumps(schema)

    def get_schema_filename(self):
        return 'attributes.schema.json'

    def get_subject_attributes(self, descriptions, subject):
        attrs = {}

        for description in descriptions:
            key = description.label
            choices = list(description.attributechoice_set.all())

            value = subject.attributes.get(description.json_key)
            if value in ['', None, ANSWER_DECLINED]:
                attrs[key] = None
            elif choices:
                if isinstance(value, list):
                    attrs[key] = []
                    for v in value:
                        choice = description.attributechoice_set.get(pk=v)
                        attrs[key].append(choice.label)
                else:
                    choice = description.attributechoice_set.get(pk=value)
                    attrs[key] = choice.label
            else:
                attrs[key] = value

        return attrs

    def get_data(self, descriptions, subjects):
        data = []

        for _id, subject in subjects:
            data.append({
                'id': str(_id),
                **self.get_subject_attributes(descriptions, subject),
            })

        return self._json_dumps(data)

    def get_data_filename(self):
        return 'attributes.json'


class BIDSExporter:
    # https://bids-specification.readthedocs.io/

    def _json_dumps(self, data):
        return json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder)

    def get_schema(self, descriptions):
        schema = {}

        for description in descriptions:
            key = description.label.lower().replace(' ', '_')
            choices = list(description.attributechoice_set.all())

            schema[key] = {k: v for k, v in [
                ('Levels', {c.id: c.label for c in choices}),
                ('Description', description.help_text),
                ('TermURL', description.url),
            ] if v}

        return self._json_dumps(schema)

    def get_schema_filename(self):
        return 'participants.json'

    def get_data(self, descriptions, subjects):
        fieldnames = ['participant_id']
        for desc in descriptions:
            key = desc.label.lower().replace(' ', '_')
            fieldnames.append(key)

        fh = StringIO()
        writer = csv.DictWriter(fh, fieldnames=fieldnames, dialect=csv.excel_tab)
        writer.writeheader()

        for _id, subject in subjects:
            row = {'participant_id': 'sub-{}'.format(_id)}
            for desc in descriptions:
                key = desc.label.lower().replace(' ', '_')
                value = subject.attributes.get(desc.json_key)
                if value in ['', None, ANSWER_DECLINED]:
                    row[key] = 'n/a'
                elif isinstance(value, list):
                    row[key] = ','.join(str(pk) for pk in value)
                else:
                    row[key] = value
            writer.writerow(row)

        return fh.getvalue()

    def get_data_filename(self):
        return 'participants.tsv'
