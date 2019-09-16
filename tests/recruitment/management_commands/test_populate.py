import pytest

from castellum.recruitment.management.commands.populate import generate_studies
from castellum.recruitment.management.commands.populate import generate_subjects
from castellum.studies.model_proxies import Study
from castellum.subjects.models import Subject


@pytest.mark.django_db
def test_generate_studies():
    generate_studies(3)
    assert Study.objects.count() == 3


@pytest.mark.django_db
def test_generate_subjects(contact_domain):
    generate_subjects(3)
    assert Subject.objects.count() == 3
