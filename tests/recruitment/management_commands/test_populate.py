from django.conf import settings

import pytest
import phonenumbers

from castellum.studies.models import Study
from castellum.pseudonyms.models import Subject
from castellum.recruitment.management.commands.populate import fake_phone_number
from castellum.recruitment.management.commands.populate import generate_studies
from castellum.recruitment.management.commands.populate import generate_subjects


@pytest.mark.django_db
def test_generate_studies():
    generate_studies(3)
    assert Study.objects.count() == 3


@pytest.mark.django_db
def test_generate_subjects():
    generate_subjects(3)
    assert Subject.objects.count() == 3


def test_phone_number_valid():
    class Pseudonym:
        pseudonym = ''

    for run in range(20):
        x = phonenumbers.parse(fake_phone_number(), settings.PHONENUMBER_DEFAULT_REGION)
        assert phonenumbers.is_valid_number(x)
