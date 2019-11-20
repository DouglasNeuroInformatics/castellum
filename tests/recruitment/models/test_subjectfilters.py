import pytest
from model_mommy import mommy

from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.studies.models import StudyType


def create_participation_request(
    subject, is_finished=False, is_exclusive=False, status=ParticipationRequest.INVITED
):
    study_status = Study.FINISHED if is_finished else Study.EXECUTION
    study = mommy.make(Study, status=study_status, is_exclusive=is_exclusive)
    return mommy.make(ParticipationRequest, status=status, subject=subject, study=study)


def has_match(is_exclusive=False, excluded_studies=[]):
    study = mommy.make(Study, is_exclusive=is_exclusive, excluded_studies=excluded_studies)
    mommy.make(SubjectFilterGroup, study=study)
    return AttributeSet.apply_study_filter(study).exists()


def test_to_q(attributeset):
    assert has_match()


def test_to_q_excluded_study(attributeset):
    pr = create_participation_request(attributeset.subject)
    assert not has_match(excluded_studies=[pr.study])


def test_to_q_excluded_study_and_unsuitable(attributeset):
    pr = create_participation_request(attributeset.subject, status=ParticipationRequest.UNSUITABLE)
    assert has_match(excluded_studies=[pr.study])


def test_to_q_excluded_study_and_unsuitable_for_other_study(attributeset):
    pr = create_participation_request(attributeset.subject)
    create_participation_request(attributeset.subject, status=ParticipationRequest.UNSUITABLE)
    assert not has_match(excluded_studies=[pr.study])


def test_to_q_reverse_excluded_study(attributeset):
    pr = create_participation_request(attributeset.subject)
    study = mommy.make(Study)
    mommy.make(SubjectFilterGroup, study=study)
    pr.study.excluded_studies.add(study)
    assert not AttributeSet.apply_study_filter(study).exists()


def test_to_q_exclusive_study(attributeset):
    assert has_match(is_exclusive=True)


def test_to_q_exclusive_study_and_finished(attributeset):
    create_participation_request(attributeset.subject, is_finished=True)
    assert has_match(is_exclusive=True)


def test_to_q_exclusive_study_in_same_study(attributeset):
    study = mommy.make(Study, is_exclusive=True)
    mommy.make(
        ParticipationRequest,
        status=ParticipationRequest.INVITED,
        subject=attributeset.subject,
        study=study,
    )
    group = mommy.make(SubjectFilterGroup, study=study)
    assert AttributeSet.objects.filter(group.to_q()).exists()


def test_to_q_exclusive_study_and_unfinished(attributeset):
    create_participation_request(attributeset.subject)
    assert not has_match(is_exclusive=True)


def test_to_q_exclusive_study_and_unsuitable(attributeset):
    create_participation_request(attributeset.subject, status=ParticipationRequest.UNSUITABLE)
    assert has_match(is_exclusive=True)


def test_to_q_other_study_exclusive_and_finished(attributeset):
    create_participation_request(attributeset.subject, is_finished=True, is_exclusive=True)
    assert has_match()


def test_to_q_other_study_is_exclusive_and_unfinished(attributeset):
    create_participation_request(attributeset.subject, is_exclusive=True)
    assert not has_match()


def test_to_q_first_study_exclusive_second_study_unfinished(attributeset):
    create_participation_request(attributeset.subject, is_finished=True, is_exclusive=True)
    create_participation_request(attributeset.subject)
    assert has_match()


def test_disinterest_in_study_type(db):
    study_type = StudyType.objects.first()
    study = mommy.make(Study)
    study.study_type.add(study_type)
    mommy.make(AttributeSet, study_type_disinterest=[study_type])
    mommy.make(SubjectFilterGroup, study=study)
    assert not AttributeSet.apply_study_filter(study).exists()


@pytest.mark.django_db
def test_clone_with_empty_filter_group(study):
    subject_filter_group = mommy.make(SubjectFilterGroup, study=study)
    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 0 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_clone_with_multiple_filters(attribute_description, study):
    subject_filter_group = mommy.make(SubjectFilterGroup, study=study)
    SubjectFilter.objects.create(group=subject_filter_group, description=attribute_description,
                                 operator="operator1", value="value1")
    SubjectFilter.objects.create(group=subject_filter_group, description=attribute_description,
                                 operator="operator2", value="value2")

    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 2 == clone.subjectfilter_set.count()
