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

from django.conf import settings
from django.core.management.base import BaseCommand

from faker import Faker

from castellum.contacts.models import Address
from castellum.contacts.models import City
from castellum.contacts.models import Contact
from castellum.contacts.models import Country
from castellum.pseudonyms.models import Pseudonym
from castellum.pseudonyms.models import Subject
from castellum.recruitment.models import AttributeSet
from castellum.studies.models import Study
from castellum.utils import FakeData

fake = Faker('de_DE')
fake_data = FakeData()


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


def fake_study():
    return Study(name=fake.word().upper(), contact_person=fake.name())


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
        contact = Contact(
            gender='f',
            first_name=fake.first_name_female(),
            last_name=fake.last_name_female(),
            birthday=fake_date_of_birth())
    else:
        contact = Contact(
            gender='m',
            first_name=fake.first_name_male(),
            last_name=fake.last_name_male(),
            birthday=fake_date_of_birth())

    if fake.random.random() < 0.67:
        contact.email = fake.email()
        contact.phone_number = fake_data.phone_number_by_probability(0.75)

    contact.pseudonym = pseudonym.pseudonym
    contact.address = address

    return contact


def fake_attributeset(pseudonym, contact):
    return AttributeSet(
        pseudonym=pseudonym.pseudonym,
        date_of_birth=contact.birthday,
        handedness='left' if fake.random.random() < 0.15 else 'right',
        first_language=fake_data.language())


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
    Subject.objects.bulk_create([Subject() for i in range(count)], batch_size=200)
    subjects = Subject.objects.all()[:count]

    contact_pseudonyms = [Pseudonym(
        subject=subjects[i], domain=settings.DOMAINS['contact']
    ) for i in range(count)]
    Pseudonym.objects.bulk_create(contact_pseudonyms)

    attributeset_pseudonyms = [Pseudonym(
        subject=subjects[i], domain=settings.DOMAINS['attributeset']
    ) for i in range(count)]
    Pseudonym.objects.bulk_create(attributeset_pseudonyms)

    print('Generating contacts')
    contacts = [fake_contact(contact_pseudonyms[i], addresses[i]) for i in range(count)]
    Contact.objects.bulk_create(contacts)

    print('Generating attributesets')
    attributesets = [
        fake_attributeset(attributeset_pseudonyms[i], contacts[i]) for i in range(count)]
    AttributeSet.objects.bulk_create(attributesets)


class Command(BaseCommand):
    help = 'Populate database with sample data.'

    def handle(self, *args, **options):
        if not Study.objects.exists():
            generate_studies(5)
        if not Contact.objects.exists():
            generate_subjects(2000)
