# (c) 2018
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

import functools
from itertools import count

from django.conf import settings
from django.core.management.base import BaseCommand

import phonenumbers
from faker import Faker

from castellum.contacts.models import Address
from castellum.contacts.models import City
from castellum.contacts.models import Contact
from castellum.contacts.models import Country
from castellum.contacts.models.contact import phonetic
from castellum.pseudonyms.models import Pseudonym
from castellum.recruitment.models import AttributeChoice
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeSet
from castellum.studies.models import Study
from castellum.subjects.models import Subject
from castellum.utils import FakeData

fake = Faker('de_DE')
fake_data = FakeData()

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
    }],
    'statistics_rank': 'secondary',
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


@functools.lru_cache(maxsize=1)
def get_highest_degree_choices():
    return AttributeChoice.objects.filter(description__pk=4).values_list('pk', flat=True)


def generate_attribute_descriptions():
    print('Generating attribute descriptions')

    for data in ATTRIBUTE_DESCRIPTIONS:
        description = AttributeDescription._import(data)
        if 'statistics_rank' in data:
            description.statistics_rank = data['statistics_rank']
            description.save()


class FakeStudy(Study):
    def __init__(self):
        study_type = fake.random.choice(Study.STUDY_TYPES)[0]

        super().__init__(
            name=fake.word().upper(),
            contact_person=fake.name(),
            min_subjects_count=fake.random.randint(0, 50),
            study_type=study_type,
            data_sensitivity = study_type == Study.FMRI,
        )


class FakeAddresses:
    def __init__(self, address_count):
        self.city_count = 100
        self.address_count = address_count

    def create(self):
        print('Generating addresses')
        germany = self.get_or_create_germany()
        self.create_cities(germany)
        self.create_addresses()

    def get_or_create_germany(self):
        country, _ = Country.objects.get_or_create(name='Deutschland')
        return country

    def create_cities(self, germany):
        city_names = set()
        while len(city_names) < self.city_count:
            city_names.add(fake.city())
        City.objects.bulk_create(City(name=city_name, country=germany) for city_name in city_names)

    def create_addresses(self):
        fake_address = lambda city_index: Address(
            city_id=fake.random.randint(1, self.city_count),
            zip_code=fake.postcode(),
            street=fake.street_name(),
            house_number=fake.random.randint(1, 200))
        Address.objects.bulk_create(list(map(fake_address, range(self.address_count))))


class FakeSubject(Subject):
    def __init__(self):
        super().__init__(privacy_level=fake.random.randint(0, 2))


class FakePseudonym(Pseudonym):
    _id = count(1)

    def __init__(self):
        super().__init__(subject_id=next(self._id), domain=Contact.domain)


class FakeContact(Contact):
    _id = count(1)

    def __init__(self, pseudonym):
        self.contact_count = next(self._id)
        gender = 'f' if fake.random.random() < 0.5 else 'm'
        first_name = fake.first_name_female() if gender == 'f' else fake.first_name_male()
        last_name = fake.last_name_female() if gender == 'f' else fake.last_name_male()
        email = fake.email() if fake.random.random() else ''
        phone_number = self.fake_phone_number() if email and fake.random.random() < 0.75 else ''

        super().__init__(
            gender=gender,
            first_name=first_name,
            first_name_phonetic=phonetic(first_name),
            last_name=last_name,
            last_name_phonetic=phonetic(last_name),
            date_of_birth=self.fake_date_of_birth(),
            email=email,
            phone_number=phone_number,
            pseudonym=pseudonym.pseudonym,
            address_id=self.contact_count,
        )

    def fake_date_of_birth(self):
        age_groups = [
            # (start age, percentage)
            (14, 0.06),
            (20, 0.14),
            (30, 0.14),
            (40, 0.16),
            (50, 0.19),
            (60, 0.14),
            (70, 0.16),
        ]

        r = fake.random.random()
        percentage = 0

        for i in range(len(age_groups) - 1):
            percentage += age_groups[i][1]

            if r < percentage:
                start_date = '-{}y'.format(age_groups[i + 1][0])
                end_date = '-{}y'.format(age_groups[i][0])
                return fake.date_between(start_date=start_date, end_date=end_date)

        start_date = '-{}y'.format(100)
        end_date = '-{}y'.format(age_groups[-1][0])
        return fake.date_between(start_date=start_date, end_date=end_date)

    def fake_phone_number(self):
        number = fake.phone_number()
        try:
            parsed = phonenumbers.parse(number, settings.PHONENUMBER_DEFAULT_REGION)
            if phonenumbers.is_valid_number(parsed):
                return number
        except phonenumbers.NumberParseException:
            pass
        # Just try again
        return self.fake_phone_number()


class FakeAttributeSet(AttributeSet):
    _id = count(1)

    def __init__(self, contact):
        super().__init__(
            subject_id=next(self._id),
            data={
                'd1': 2 if fake.random.random() < 0.15 else 1,
                'd2': fake_data.language(),
                'd3': contact.date_of_birth,
                'd4': fake.random.choice(get_highest_degree_choices()),
            }
        )


class Command(BaseCommand):
    help = 'Populate database with sample data.'

    def add_arguments(self, parser):
        parser.add_argument('--study-count', action='store', nargs='?', default=5)
        parser.add_argument('--subject-count', action='store', nargs='?', default=2000)

    def handle(self, *args, **options):
        if not AttributeDescription.objects.exists():
            generate_attribute_descriptions()

        self.create_studies(options['study_count'])
        self.create_subjects(options['subject_count'])

    def create_studies(self, study_count):
        if Study.objects.exists():
            return

        print('Generating studies')
        Study.objects.bulk_create(FakeStudy() for _ in range(study_count))

    def create_subjects(self, subject_count):
        if Subject.objects.exists():
            return

        fake_addresses = FakeAddresses(address_count=subject_count)
        fake_addresses.create()

        print('Generating subjects')
        Subject.objects.bulk_create([FakeSubject() for _ in range(subject_count)])

        print('Generating pseudonyms')
        pseudonyms = [FakePseudonym() for _ in range(subject_count)]
        Pseudonym.objects.bulk_create(pseudonyms)

        print('Generating contacts')
        contacts = [FakeContact(pseudonyms[i]) for i in range(subject_count-1)]
        contacts.append(Contact(
            pseudonym=pseudonyms[-1].pseudonym,
            gender='*',
            first_name='Muhammad',
            first_name_phonetic=phonetic('Muhammad'),
            last_name='Nguyen',
            last_name_phonetic=phonetic('Nguyen'),
            date_of_birth='2000-12-13',
            email='muhammad@example.com',
        ))
        Contact.objects.bulk_create(contacts)

        print('Generating attributesets')
        attributesets = [FakeAttributeSet(contacts[i]) for i in range(subject_count)]
        AttributeSet.objects.bulk_create(attributesets)
