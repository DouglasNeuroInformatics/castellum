# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
        return json.dumps(
            data, sort_keys=True, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder
        )

    def get_schema(self, attributes):
        schema = {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'string',
                },
                'privacy_level': {
                    'type': 'integer',
                    'enum': [0, 1, 2],
                },
            },
        }

        for attribute in attributes:
            key = attribute.label

            data = {k: v for k, v in [
                ('type', self.TYPES.get(attribute.field_type, 'string')),
                ('format', self.FORMATS.get(attribute.field_type)),
                ('description', attribute.help_text),
            ] if v}

            if attribute.field_type in ['ChoiceField', 'OrderedChoiceField']:
                data['enum'] = [c.label for c in attribute.attributechoice_set.all()]
            elif attribute.field_type == 'MultipleChoiceField':
                data['items'] = {
                    'type': 'string',
                    'enum': [c.label for c in attribute.attributechoice_set.all()],
                }

            schema['properties'][key] = data

        return self._json_dumps(schema)

    def get_schema_filename(self):
        return 'attributes.schema.json'

    def get_subject_attributes(self, attributes, subject):
        data = {}

        for attribute in attributes:
            key = attribute.label
            value = subject.attributes.get(attribute.json_key)
            if value in ['', None, ANSWER_DECLINED]:
                data[key] = None
            elif attribute.field_type in ['ChoiceField', 'OrderedChoiceField']:
                data[key] = attribute.attributechoice_set.get(pk=value).label
            elif attribute.field_type == 'MultipleChoiceField':
                choices = {c.id: c.label for c in attribute.attributechoice_set.all()}
                data[key] = [choices[v] for v in value]
            else:
                data[key] = value

        data['privacy_level'] = subject.get_effective_privacy_level()

        return data

    def get_data(self, attributes, subjects):
        data = []

        for _id, subject in subjects:
            data.append({
                'id': str(_id),
                **self.get_subject_attributes(attributes, subject),
            })

        return self._json_dumps(data)

    def get_data_filename(self):
        return 'attributes.json'


class BIDSExporter:
    # https://bids-specification.readthedocs.io/

    def _json_dumps(self, data):
        return json.dumps(
            data, sort_keys=True, indent=4, ensure_ascii=False, cls=DjangoJSONEncoder
        )

    def get_schema(self, attributes):
        schema = {}

        for attribute in attributes:
            key = attribute.label.lower().replace(' ', '_')

            schema[key] = {k: v for k, v in [
                ('Description', attribute.help_text),
                ('TermURL', attribute.url),
            ] if v}

            if attribute.field_type in [
                'ChoiceField', 'MultipleChoiceField', 'OrderedChoiceField'
            ]:
                choices = {c.id: c.label for c in attribute.attributechoice_set.all()}
                schema[key]['Levels'] = choices

        schema['privacy_level'] = {
            'Levels': {
                0: 'regular',
                1: 'increased',
                2: 'high',
            },
        }

        return self._json_dumps(schema)

    def get_schema_filename(self):
        return 'participants.json'

    def get_data(self, attributes, subjects):
        fieldnames = ['participant_id', 'privacy_level']
        for attribute in attributes:
            key = attribute.label.lower().replace(' ', '_')
            fieldnames.append(key)

        fh = StringIO()
        writer = csv.DictWriter(fh, fieldnames=fieldnames, dialect=csv.excel_tab)
        writer.writeheader()

        for _id, subject in subjects:
            row = {
                'participant_id': f'sub-{_id}',
                'privacy_level': subject.get_effective_privacy_level(),
            }
            for attribute in attributes:
                key = attribute.label.lower().replace(' ', '_')
                value = subject.attributes.get(attribute.json_key)
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
