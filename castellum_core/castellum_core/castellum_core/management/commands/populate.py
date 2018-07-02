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

from django.core.management.base import BaseCommand

from faker import Faker

from studies.models import Study
from subject_management.models import Address
from subject_management.models import City
from subject_management.models import Country
from subject_management.models import Subject

fake = Faker('de_DE')


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


def fake_address(country):
    city, __ = City.objects.get_or_create(name=fake.city(), country=country)
    return Address(
        city=city,
        zip_code=fake.postcode(),
        street=fake.street_name(),
        house_number=fake.random.randint(1, 200))


def fake_subject(address):
    if fake.random.random() < 0.5:
        subject = Subject(
            gender='f',
            first_name=fake.first_name_female(),
            last_name=fake.last_name_female(),
            birthday=fake_date_of_birth())
    else:
        subject = Subject(
            gender='m',
            first_name=fake.first_name_male(),
            last_name=fake.last_name_male(),
            birthday=fake_date_of_birth())

    if fake.random.random() < 0.67:
        subject.email = fake.email()
        if fake.random.random() < 0.75:
            subject.phone_number = fake.phone_number()

    subject.address = address

    return subject


class Command(BaseCommand):
    help = 'Populate database with sample data.'

    def handle(self, *args, **options):
        Study.objects.bulk_create(fake_study() for i in range(5))

        country, __ = Country.objects.get_or_create(name='Deutschland')
        addresses = [fake_address(country) for i in range(2000)]
        Address.objects.bulk_create(addresses)
        Subject.objects.bulk_create(fake_subject(address) for address in addresses)
