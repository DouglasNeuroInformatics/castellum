import pytest

from castellum.studies.models import Study
from castellum.subjects.models import Subject
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
