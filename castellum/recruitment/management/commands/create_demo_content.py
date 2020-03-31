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

import functools

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

import phonenumbers
from faker import Faker
from huscy.projects.models import Project
from huscy.projects.models import ResearchUnit

from castellum.castellum_auth.models import User
from castellum.contacts.models import Address
from castellum.contacts.models import Contact
from castellum.contacts.models import phonetic
from castellum.recruitment.models import AttributeChoice
from castellum.recruitment.models import AttributeSet
from castellum.studies.models import Study
from castellum.studies.models import StudyType
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
    return Subject(privacy_level=fake.random.randint(0, 2))


def fake_project(dummy_user, dummy_unit, local_id):
    return Project(
        title=fake.word().upper(),
        description=fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
        research_unit=dummy_unit,
        principal_investigator=dummy_user,
        local_id=local_id,
    )


def fake_study(project):
    recruitment_text = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
    study = Study(
        project=project,
        contact_person=fake.name(),
        principal_investigator=fake.name(),
        min_subject_count=fake.random.randint(0, 50),
        recruitment_text=recruitment_text,
        expense_allowance=fake.random.randint(20, 50),
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

    contact = Contact(
        gender=gender,
        first_name=first_name,
        first_name_phonetic=phonetic(first_name),
        last_name=last_name,
        last_name_phonetic=phonetic(last_name),
        date_of_birth=fake_date_of_birth(),
        subject_id=subject.pk,
    )

    if fake.random.random() < 0.67:
        contact.email = fake.email()
        if fake.random.random() < 0.75:
            contact.phone_number = fake_phone_number()

    return contact


def fake_attributeset(subject, contact):
    data = {}
    if fake.random.random() < 0.9:
        data['d1'] = 2 if fake.random.random() < 0.15 else 1
    if fake.random.random() < 0.9:
        data['d2'] = fake_language()
    if fake.random.random() < 0.9:
        data['d3'] = contact.date_of_birth
    if fake.random.random() < 0.9:
        data['d4'] = fake.random.choice(get_highest_degree_choices())
    return AttributeSet(subject=subject, data=data)


def generate_studies(count):
    print('Generating studies')
    dummy_user, __ = User.objects.get_or_create(username='dummy')
    dummy_unit, __ = ResearchUnit.objects.get_or_create(
        name='dummy', code='dummy', principal_investigator=dummy_user
    )
    Project.objects.bulk_create(fake_project(dummy_user, dummy_unit, i + 1) for i in range(count))
    projects = Project.objects.all()[:count]

    studies = [fake_study(project) for project in projects]
    for study in studies:
        study.save()

    study_types = list(StudyType.objects.all())
    for study in studies:
        study.study_type.add(fake.random.choice(study_types))


def generate_subjects(count):
    # NOTE: We have ForeignKeys to Address and Subject. Unfortunately, bulk_create does not set
    # the id on the instances, so we have to get them from the database after bulk_create. This
    # assumes that the database was empty before.

    print('Generating pseudonyms')
    Subject.objects.bulk_create([fake_subject() for i in range(count)], batch_size=200)
    subjects = Subject.objects.all()[:count]

    print('Generating contacts')
    contacts = [fake_contact(subjects[i]) for i in range(count-1)]
    testcontact = Contact(
        gender='*',
        first_name='Muhammad',
        first_name_phonetic=phonetic('Muhammad'),
        last_name='Nguyen',
        last_name_phonetic=phonetic('Nguyen'),
        date_of_birth='2000-12-13',
        email='muhammad@example.com',
        subject_id=subjects[count - 1].pk,
    )
    contacts.append(testcontact)

    Contact.objects.bulk_create(contacts)
    contacts = Contact.objects.all()[:count]

    print('Generating addresses')
    Address.objects.bulk_create(fake_address(contact) for contact in contacts)

    print('Generating attributesets')
    attributesets = [fake_attributeset(subjects[i], contacts[i]) for i in range(count)]
    AttributeSet.objects.bulk_create(attributesets)


class Command(BaseCommand):
    help = 'Populate database with demo data.'

    def add_arguments(self, parser):
        parser.add_argument('--study-count', default=5, type=int)
        parser.add_argument('--subject-count', default=2000, type=int)

    def handle(self, *args, **options):
        if settings.PRODUCTION:
            raise CommandError('Demo content not created in production environment.')

        if not Study.objects.exists():
            generate_studies(options['study_count'])
        if not Subject.objects.exists():
            generate_subjects(options['subject_count'])
