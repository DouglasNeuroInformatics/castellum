import pytest
from model_mommy import mommy

from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study


def create_participation_request(
    subject, is_finished=False, is_exclusive=False, status=ParticipationRequest.INVITED
):
    study_mode = Study.FINISHED if is_finished else Study.EXECUTION
    study = mommy.make(Study, study_mode=study_mode, is_exclusive=is_exclusive)
    return mommy.make(
        ParticipationRequest, status=status, subject=subject, group=study.default_group
    )


def has_match(is_exclusive=False, excluded_studies=[]):
    study = mommy.make(Study, is_exclusive=is_exclusive)
    group = mommy.make(SubjectFilterGroup, study=study, excluded_studies=excluded_studies)
    return AttributeSet.objects.filter(group.to_q()).exists()


def test_to_q(attributeset):
    assert has_match()


def test_to_q_excluded_study(attributeset):
    pr = create_participation_request(attributeset.subject)
    assert not has_match(excluded_studies=[pr.group.study])


def test_to_q_excluded_study_and_unsuitable(attributeset):
    pr = create_participation_request(attributeset.subject, status=ParticipationRequest.UNSUITABLE)
    assert has_match(excluded_studies=[pr.group.study])


def test_to_q_excluded_study_and_unsuitable_for_other_study(attributeset):
    pr = create_participation_request(attributeset.subject)
    create_participation_request(attributeset.subject, status=ParticipationRequest.UNSUITABLE)
    assert not has_match(excluded_studies=[pr.group.study])


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
        group=study.default_group,
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
