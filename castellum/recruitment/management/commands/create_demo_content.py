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

import functools

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import IntegrityError

import phonenumbers
from faker import Faker

from castellum.contacts.models import Address
from castellum.contacts.models import Contact
from castellum.contacts.models import Street
from castellum.contacts.models import phonetic
from castellum.pseudonyms.models import CodingList
from castellum.recruitment.models import AttributeChoice
from castellum.studies.models import Study
from castellum.studies.models import StudySession
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument
from castellum.subjects.models import Subject

fake = Faker('de_DE')


@functools.lru_cache(maxsize=1)
def get_highest_degree_choices():
    return AttributeChoice.objects.filter(description__pk=4).values_list('pk', flat=True)


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


def fake_language():
    groups = [
        # (language, percentage)
        ('de', 0.70),
        ('en', 0.10),
        ('tr', 0.06),
        ('fr', 0.06),
        ('es', 0.06),
        ('it', 0.02),
    ]

    r = fake.random.random()
    percentage = 0

    for lang, p in groups:
        percentage += p

        if r < percentage:
            return lang

    return groups[-1][0]


def fake_subject():
    return Subject(privacy_level=fake.random.randint(0, 2), attributes=fake_attributes())


def fake_studysession(study):
    return StudySession(study=study, name=fake.word(), duration=fake.random.randrange(10, 120, 10))


def fake_study():
    description = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
    recruitment_text = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
    study = Study(
        name=fake.word().upper(),
        contact_person=fake.name(),
        email=fake.email(),
        phone=fake_phone_number(),
        principal_investigator=fake.name(),
        min_subject_count=fake.random.randint(0, 50),
        description=description,
        recruitment_text=recruitment_text,
        sessions_start=fake.past_date(start_date="-30d"),
        sessions_end=fake.future_date(end_date="+30d"),
    )
    return study


def fake_address(contact):
    return Address(
        contact=contact,
        country='Deutschland',
        city=fake.city(),
        zip_code=fake.postcode(),
        street=fake.street_name(),
        house_number=fake.random.randint(1, 200),
    )


def fake_contact(subject):
    if fake.random.random() < 0.5:
        gender = 'f'
        first_name = fake.first_name_female()
        last_name = fake.last_name_female()
    else:
        gender = 'm'
        first_name = fake.first_name_male()
        last_name = fake.last_name_male()

    if settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID:
        key = 'd{}'.format(settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID)
        date_of_birth = subject.attributes.get(key)
    else:
        date_of_birth = fake_date_of_birth()

    contact = Contact(
        gender=gender,
        first_name=first_name,
        first_name_phonetic=phonetic(first_name),
        last_name=last_name,
        last_name_phonetic=phonetic(last_name),
        date_of_birth=date_of_birth,
        subject_uuid=subject.uuid,
    )

    if fake.random.random() < 0.67:
        contact.email = fake.email()
        if fake.random.random() < 0.75:
            contact.phone_number = fake_phone_number()

    return contact


def fake_attributes():
    data = {}
    if fake.random.random() < 0.9:
        data['d1'] = 2 if fake.random.random() < 0.15 else 1
    if fake.random.random() < 0.9:
        data['d2'] = fake_language()
    if fake.random.random() < 0.9:
        data['d3'] = fake_date_of_birth()
    if fake.random.random() < 0.9:
        data['d4'] = fake.random.choice(get_highest_degree_choices())
    return data


def generate_geolocations(contacts):
    from castellum.geofilters.models import Geolocation

    Geolocation.objects.bulk_create(Geolocation(
        contact=contact,
        point=Point(
            fake.random.uniform(13.2378, 13.6224),
            fake.random.uniform(52.4085, 52.5753),
        ),
    ) for contact in contacts)


def generate_studies(count, stdout):
    stdout.write('Generating studies')
    i = 0
    while i < count:
        study = fake_study()
        try:
            study.save()
        except IntegrityError:
            continue
        i += 1

        CodingList.objects.create(
            bits=settings.CASTELLUM_STUDY_PSEUDONYM_BITS,
            context=study,
        )

        session = fake_studysession(study)
        session.save()
        for name, color in settings.CASTELLUM_DEFAULT_EXECUTION_TAGS:
            study.executiontag_set.create(name=name, color=color)


def generate_subjects(count, stdout):
    # NOTE: We have ForeignKeys to Address and Subject. Unfortunately, bulk_create does not set
    # the id on the instances, so we have to get them from the database after bulk_create. This
    # assumes that the database was empty before.

    stdout.write('Generating subjects')
    Subject.objects.bulk_create([fake_subject() for i in range(count)], batch_size=200)
    subjects = Subject.objects.all()[:count]

    stdout.write('Generating contacts')
    contacts = [fake_contact(subjects[i]) for i in range(count)]
    contacts[-1].first_name = 'Muhammad'
    contacts[-1].first_name_phonetic = phonetic('Muhammad')
    contacts[-1].last_name = 'Nguyen'
    contacts[-1].last_name_phonetic = phonetic('Nguyen')
    contacts[-1].email = 'muhammad@example.com'

    Contact.objects.bulk_create(contacts)
    contacts = Contact.objects.all()[:count]

    stdout.write('Generating addresses')
    Address.objects.bulk_create(fake_address(contact) for contact in contacts)

    if 'castellum.geofilters' in settings.INSTALLED_APPS:
        stdout.write('Generating geolocations')
        generate_geolocations(contacts)

    stdout.write('Generating consents')
    document = ConsentDocument.get_latest()
    consents = [Consent(subject=s, document=document, status=Consent.CONFIRMED) for s in subjects]
    Consent.objects.bulk_create(consents)


def generate_streets(count, stdout):
    stdout.write('Generating streets')
    streets = [Street(name=fake.street_name()) for i in range(count)]
    Street.objects.bulk_create(streets, batch_size=200)


class Command(BaseCommand):
    help = 'Populate database with demo data.'

    def add_arguments(self, parser):
        parser.add_argument('--study-count', default=5, type=int)
        parser.add_argument('--subject-count', default=2000, type=int)
        parser.add_argument('--street-count', default=1000, type=int)

    def handle(self, *args, **options):
        if settings.PRODUCTION:
            raise CommandError('Demo content not created in production environment.')

        if not Study.objects.exists():
            generate_studies(options['study_count'], self.stdout)
        if not Subject.objects.exists():
            generate_subjects(options['subject_count'], self.stdout)
        if not Street.objects.exists():
            generate_streets(options['street_count'], self.stdout)
