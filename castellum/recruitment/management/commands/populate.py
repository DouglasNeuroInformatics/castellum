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


def fake_date_of_birth():
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


def fake_phone_number():
    number = fake.phone_number()
    try:
        parsed = phonenumbers.parse(number, settings.PHONENUMBER_DEFAULT_REGION)
        if phonenumbers.is_valid_number(parsed):
            return number
    except phonenumbers.NumberParseException:
        pass
    # Just try again
    return fake_phone_number()


def fake_subject():
    return Subject(privacy_level=fake.random.randint(0, 2))


def fake_study():
    study = Study(
        name=fake.word().upper(),
        contact_person=fake.name(),
        min_subjects_count=fake.random.randint(0, 50),
        study_type=fake.random.choice(Study.STUDY_TYPES)[0])
    if study.study_type == Study.FMRI:
        study.data_sensitivity = True
    return study


def fake_cities(country, count):
    names = set()
    while len(names) < count:
        names.add(fake.city())
    return [City(name=name, country=country) for name in names]


def fake_address(cities):
    return Address(
        city=fake.random.choice(cities),
        zip_code=fake.postcode(),
        street=fake.street_name(),
        house_number=fake.random.randint(1, 200))


def fake_contact(pseudonym, address):
    if fake.random.random() < 0.5:
        gender = 'f'
        first_name = fake.first_name_female()
        last_name = fake.last_name_female()
    else:
        gender = 'm'
        first_name = fake.first_name_male()
        last_name = fake.last_name_male()

    contact = Contact(
        gender=gender,
        first_name=first_name,
        first_name_phonetic=phonetic(first_name),
        last_name=last_name,
        last_name_phonetic=phonetic(last_name),
        date_of_birth=fake_date_of_birth())

    if fake.random.random() < 0.67:
        contact.email = fake.email()
        if fake.random.random() < 0.75:
            contact.phone_number = fake_phone_number()

    contact.pseudonym = pseudonym.pseudonym
    contact.address = address

    return contact


@functools.lru_cache(maxsize=1)
def get_highest_degree_choices():
    return AttributeChoice.objects.filter(description__pk=4).values_list('pk', flat=True)


def fake_attributeset(subject, contact):
    return AttributeSet(
        subject=subject,
        data={
            'd1': 2 if fake.random.random() < 0.15 else 1,
            'd2': fake_data.language(),
            'd3': contact.date_of_birth,
            'd4': fake.random.choice(get_highest_degree_choices()),
        })


def generate_attribute_descriptions():
    print('Generating attribute descriptions')

    for data in ATTRIBUTE_DESCRIPTIONS:
        description = AttributeDescription._import(data)
        if 'statistics_rank' in data:
            description.statistics_rank = data['statistics_rank']
            description.save()


def generate_studies(count):
    print('Generating studies')
    Study.objects.bulk_create(fake_study() for i in range(count))


def generate_subjects(count):
    # NOTE: We have ForeignKeys to Address and Subject. Unfortunately, bulk_create does not set
    # the id on the instances, so we have to get them from the database after bulk_create. This
    # assumes that the database was empty before.

    print('Generating addresses')
    country, __ = Country.objects.get_or_create(name='Deutschland')
    City.objects.bulk_create(fake_cities(country, 100))
    cities = City.objects.all()[:100]
    Address.objects.bulk_create(fake_address(cities) for i in range(count))
    addresses = Address.objects.all()[:count]

    print('Generating pseudonyms')
    Subject.objects.bulk_create([fake_subject() for i in range(count)], batch_size=200)
    subjects = Subject.objects.all()[:count]

    contact_pseudonyms = [Pseudonym(
        subject=subjects[i], domain=Contact.domain
    ) for i in range(count)]
    Pseudonym.objects.bulk_create(contact_pseudonyms)

    print('Generating contacts')
    contacts = [fake_contact(contact_pseudonyms[i], addresses[i]) for i in range(count-1)]
    testcontact = Contact(
        gender='*',
        first_name='Muhammad',
        first_name_phonetic=phonetic('Muhammad'),
        last_name='Nguyen',
        last_name_phonetic=phonetic('Nguyen'),
        date_of_birth='2000-12-13',
        email='muhammad@example.com',
    )
    contacts.append(testcontact)
    testcontact.pseudonym = contact_pseudonyms[-1]

    Contact.objects.bulk_create(contacts)

    print('Generating attributesets')
    attributesets = [
        fake_attributeset(subjects[i], contacts[i])
        for i in range(count)
    ]
    AttributeSet.objects.bulk_create(attributesets)


class Command(BaseCommand):
    help = 'Populate database with sample data.'

    def handle(self, *args, **options):
        if not AttributeDescription.objects.exists():
            generate_attribute_descriptions()
        if not Study.objects.exists():
            generate_studies(5)
        if not Contact.objects.exists():
            generate_subjects(2000)
