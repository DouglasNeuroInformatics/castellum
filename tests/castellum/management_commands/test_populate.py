import pytest

from castellum.studies.models import Study
from castellum.pseudonyms.models import Subject
from castellum.pseudonyms.management import generate_studies
from castellum.pseudonyms.management import generate_subjects


@pytest.mark.django_db
def test_generate_studies():
    generate_studies(3)
    assert Study.objects.count() == 3


@pytest.mark.django_db
def test_generate_subjects():
    generate_subjects(3)
    assert Subject.objects.count() == 3
