import pytest

from studies.models import Study
from pseudonyms.models import Subject
from castellum.management.commands.populate import generate_studies
from castellum.management.commands.populate import generate_subjects


@pytest.mark.django_db
def test_generate_studies():
    generate_studies(3)
    assert Study.objects.count() == 3


@pytest.mark.django_db
def test_generate_subjects():
    generate_subjects(3)
    assert Subject.objects.count() == 3
