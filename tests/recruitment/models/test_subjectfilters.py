import pytest
from model_bakery import baker

from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.studies.models import StudySession
from castellum.studies.models import StudyType
from castellum.subjects.models import Subject


def create_participation(
    subject, is_finished=False, is_exclusive=False, status=Participation.INVITED
):
    study_status = Study.FINISHED if is_finished else Study.EXECUTION
    study = baker.make(Study, status=study_status, is_exclusive=is_exclusive)
    return baker.make(Participation, status=status, subject=subject, study=study)


def has_match(is_exclusive=False, excluded_studies=[]):
    study = baker.make(Study, is_exclusive=is_exclusive, excluded_studies=excluded_studies)
    baker.make(SubjectFilterGroup, study=study)
    return Subject.objects.filter(filter_queries.study(study)).exists()


def test_to_q(subject):
    assert has_match()


def test_to_q_excluded_study(subject):
    participation = create_participation(subject)
    assert not has_match(excluded_studies=[participation.study])


def test_to_q_excluded_study_and_unsuitable(subject):
    participation = create_participation(subject, status=Participation.UNSUITABLE)
    assert has_match(excluded_studies=[participation.study])


def test_to_q_excluded_study_and_unsuitable_for_other_study(subject):
    participation = create_participation(subject)
    create_participation(subject, status=Participation.UNSUITABLE)
    assert not has_match(excluded_studies=[participation.study])


def test_to_q_reverse_excluded_study(subject):
    participation = create_participation(subject)
    study = baker.make(Study)
    participation.study.excluded_studies.add(study)
    assert not Subject.objects.filter(filter_queries.study(study)).exists()


def test_to_q_exclusive_study(subject):
    assert has_match(is_exclusive=True)


def test_to_q_exclusive_study_and_finished(subject):
    create_participation(subject, is_finished=True)
    assert has_match(is_exclusive=True)


def test_to_q_exclusive_study_in_same_study(subject):
    study = baker.make(Study, is_exclusive=True)
    baker.make(
        Participation,
        status=Participation.INVITED,
        subject=subject,
        study=study,
    )
    q = filter_queries.study_exclusion(study)
    assert Subject.objects.filter(q).exists()


def test_to_q_exclusive_study_and_unfinished(subject):
    create_participation(subject)
    assert not has_match(is_exclusive=True)


def test_to_q_exclusive_study_and_unsuitable(subject):
    create_participation(subject, status=Participation.UNSUITABLE)
    assert has_match(is_exclusive=True)


def test_to_q_other_study_exclusive_and_finished(subject):
    create_participation(subject, is_finished=True, is_exclusive=True)
    assert has_match()


def test_to_q_other_study_is_exclusive_and_unfinished(subject):
    create_participation(subject, is_exclusive=True)
    assert not has_match()


def test_to_q_first_study_exclusive_second_study_unfinished(subject):
    create_participation(subject, is_finished=True, is_exclusive=True)
    create_participation(subject)
    assert has_match()


def test_disinterest_in_study_type(db):
    study_type = StudyType.objects.first()
    study = baker.make(Study)
    session = baker.make(StudySession, study=study)
    session.type.add(study_type)
    baker.make(Subject, study_type_disinterest=[study_type])
    assert not Subject.objects.filter(filter_queries.study(study)).exists()


@pytest.mark.django_db
def test_clone_with_empty_filter_group(study):
    subject_filter_group = baker.make(SubjectFilterGroup, study=study)
    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 0 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_clone_with_multiple_filters(attribute_description, study):
    subject_filter_group = baker.make(SubjectFilterGroup, study=study)
    SubjectFilter.objects.create(
        group=subject_filter_group,
        description=attribute_description,
        operator="operator1",
        value="value1",
    )
    SubjectFilter.objects.create(
        group=subject_filter_group,
        description=attribute_description,
        operator="operator2",
        value="value2",
    )

    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 2 == clone.subjectfilter_set.count()
