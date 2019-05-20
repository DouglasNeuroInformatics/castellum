import pytest

from castellum.studies.models import Study
from castellum.subjects.models import Subject
from castellum.recruitment.management.commands.populate import Command


@pytest.mark.django_db
def test_generate_studies():
    command = Command()
    command.handle(study_count=3, subject_count=0)
    assert Study.objects.count() == 3


@pytest.mark.django_db
def test_generate_subjects():
    command = Command()
    command.handle(study_count=0, subject_count=3)
    assert Subject.objects.count() == 3
