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

from django.core.management.base import BaseCommand

from castellum.recruitment.models import AttributeDescription

ATTRIBUTE_DESCRIPTIONS = [{
    'field_type': 'ChoiceField',
    'order': 0,
    'label': {
        'de': 'Händigkeit',
        'en': 'Handedness',
    },
    'choices': [{
        'label': {
            'de': 'Rechts',
            'en': 'Right',
        }
    }, {
        'label': {
            'de': 'Links',
            'en': 'Left',
        }
    }, {
        'label': {
            'de': 'Beidhändig',
            'en': 'Ambidextrous',
        }
    }],
    'statistics_rank': 'secondary',
    'url': 'http://purl.bioontology.org/ontology/SNOMEDCT/57427004',
}, {
    'field_type': 'CharField',
    'order': 1,
    'label': {
        'de': 'Muttersprache',
        'en': 'Language',
    },
}, {
    'field_type': 'AgeField',
    'order': 2,
    'label': {
        'de': 'Geburtsdatum',
        'en': 'Date of birth',
    },
    '_filter_label': {
        'de': 'Alter',
        'en': 'Age',
    },
    'statistics_rank': 'primary',
    'url': 'http://purl.bioontology.org/ontology/SNOMEDCT/397669002',
}, {
    'field_type': 'OrderedChoiceField',
    'order': 3,
    'label': {
        'de': 'Höchster Abschluss',
        'en': 'Highest degree',
    },
    'choices': [{
        'label': {
            'de': 'Kein Abschluss',
            'en': 'No degree',
        }
    }, {
        'label': {
            'de': 'Grundschule',
            'en': 'Elementary school',
        }
    }, {
        'label': {
            'de': 'Hauptschule',
            'en': 'Hauptschule',
        }
    }, {
        'label': {
            'de': 'Mittlere Reife',
            'en': 'Mittlere Reife',
        }
    }, {
        'label': {
            'de': 'Abitur',
            'en': 'Abitur',
        }
    }, {
        'label': {
            'de': 'Bachelor',
            'en': 'Bachelor',
        }
    }, {
        'label': {
            'de': 'Master',
            'en': 'Master',
        }
    }],
}]


def generate_attribute_descriptions():
    for data in ATTRIBUTE_DESCRIPTIONS:
        description = AttributeDescription._import(data)
        if 'statistics_rank' in data:
            description.statistics_rank = data['statistics_rank']
            description.save()


class Command(BaseCommand):
    help = 'Create recommended AttributeDescriptions.'

    def handle(self, *args, **options):
        if not AttributeDescription.objects.exists():
            generate_attribute_descriptions()
