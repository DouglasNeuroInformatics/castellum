import datetime

from model_bakery import baker

from castellum.recruitment.models import SubjectFilter
from castellum.studies.models import Study
from castellum.studies.views.recruitment import get_conflicting_studies


def test_conflicting_studies(subject):
    study = baker.make(
        Study,
        sessions_start=datetime.date(2000, 1, 1),
        sessions_end=datetime.date(2000, 3, 1),
    )

    other = baker.make(
        Study,
        min_subject_count=1,
        sessions_start=datetime.date(2000, 1, 1),
        sessions_end=datetime.date(2000, 3, 1),
    )

    assert other in get_conflicting_studies(study)


def test_conflicting_studies_filter(subject, attribute_description):
    subject.attributes[attribute_description.json_key] = 1
    subject.save()

    study = baker.make(
        Study,
        sessions_start=datetime.date(2000, 1, 1),
        sessions_end=datetime.date(2000, 3, 1),
    )
    baker.make(
        SubjectFilter,
        group__study=study,
        description=attribute_description,
        operator='exact',
        value=1,
    )

    other = baker.make(
        Study,
        min_subject_count=1,
        sessions_start=datetime.date(2000, 1, 1),
        sessions_end=datetime.date(2000, 3, 1),
    )
    baker.make(
        SubjectFilter,
        group__study=other,
        description=attribute_description,
        operator='exact',
        value=2,
    )

    assert other not in get_conflicting_studies(study)


def test_conflicting_studies_time(subject):
    study = baker.make(
        Study,
        sessions_start=datetime.date(2000, 1, 1),
        sessions_end=datetime.date(2000, 3, 1),
    )

    other = baker.make(
        Study,
        min_subject_count=1,
        sessions_start=datetime.date(2000, 4, 1),
        sessions_end=datetime.date(2000, 5, 1),
    )

    assert other not in get_conflicting_studies(study)
