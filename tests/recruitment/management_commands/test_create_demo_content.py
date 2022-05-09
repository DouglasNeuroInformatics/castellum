import sys

import pytest

from castellum.recruitment.management.commands.create_demo_content import generate_studies
from castellum.recruitment.management.commands.create_demo_content import generate_subjects
from castellum.studies.models import Study
from castellum.subjects.models import Subject


@pytest.mark.django_db
def test_generate_studies():
    generate_studies(3, sys.stdout)
    assert Study.objects.count() == 3


@pytest.mark.django_db
def test_generate_subjects():
    generate_subjects(6, sys.stdout)
    assert Subject.objects.count() == 6
