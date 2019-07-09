from itertools import cycle

import pytest
from model_mommy import mommy

from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.models import Study


"""
- create five studies (1-5)
- create one subject filter group for study 1
- create 4 subjects with attribute_sets
- subject 1 participates in study 2
- subject 2 participates in studies 2 and 3
- subject 3 participates in studies 2, 3 and 4
- subject 4 participates in studies 2, 3, 4 and 5
"""


def pr_for_exclusive_studies(attributesets, is_finished, is_exclusive):
    if is_finished:
        study_mode = Study.FINISHED
    else:
        study_mode = Study.RECRUITMENT

    study = mommy.make('studies.Study', study_mode=study_mode, is_exclusive=is_exclusive)
    return mommy.make(
        ParticipationRequest,
        status=ParticipationRequest.INVITED,
        subject=attributesets[0].subject,
        study=study,
    )


def subject_filter_group_exclusive_study(is_exclusive):
    study = mommy.make('studies.Study', study_mode=Study.RECRUITMENT, is_exclusive=is_exclusive)
    return mommy.make(
            'recruitment.SubjectFilterGroup',
            study=study,
    )


@pytest.fixture
def five_studies():
    return mommy.make('studies.Study', _quantity=5)


@pytest.fixture
def subject_filter_group(five_studies):
    return mommy.make('recruitment.SubjectFilterGroup', study=five_studies[0])


@pytest.fixture
def attributesets(contact):
    return mommy.make(AttributeSet, data=dict(d1=1), _quantity=4)


@pytest.fixture
def participation_requests(attributesets, five_studies):
    invited = ParticipationRequest.INVITED
    mommy.make(ParticipationRequest, status=invited, subject=attributesets[0].subject,
               study=five_studies[1])
    mommy.make(ParticipationRequest, status=invited, subject=attributesets[1].subject,
               study=cycle(five_studies[1:3]), _quantity=2)
    mommy.make(ParticipationRequest, status=invited, subject=attributesets[2].subject,
               study=cycle(five_studies[1:4]), _quantity=3)
    mommy.make(ParticipationRequest, status=invited, subject=attributesets[3].subject,
               study=cycle(five_studies[1:5]), _quantity=4)


@pytest.mark.django_db
def test_to_q_with_no_excluded_studies(subject_filter_group, participation_requests):
    q = subject_filter_group.to_q()
    result = AttributeSet.objects.filter(q)
    assert len(result) == 4


@pytest.mark.django_db
@pytest.mark.parametrize("excluded_study_idx,expected_subjects", [
    (1, 0),
    (2, 1),
    (3, 2),
    (4, 3),
])
def test_to_q_with_one_excluded_study(excluded_study_idx, expected_subjects,
                                      five_studies, subject_filter_group, participation_requests):
    excluded_study = five_studies[excluded_study_idx]
    subject_filter_group.excluded_studies.add(excluded_study)
    subject_filter_group.save()

    q = subject_filter_group.to_q()
    result = AttributeSet.objects.filter(q)
    assert len(result) == expected_subjects


@pytest.mark.django_db
@pytest.mark.parametrize("excluded_study_idx,expected_subjects", [
    (1, 0),
    (2, 1),
    (3, 4),
    (4, 3),
])
def test_to_q_when_subjects_are_unsuitable_for_other_study(excluded_study_idx, expected_subjects,
                                                           five_studies, subject_filter_group,
                                                           participation_requests):
    unsuitable = ParticipationRequest.UNSUITABLE
    ParticipationRequest.objects.filter(study=five_studies[3]).update(status=unsuitable)

    excluded_study = five_studies[excluded_study_idx]
    subject_filter_group.excluded_studies.add(excluded_study)
    subject_filter_group.save()

    q = subject_filter_group.to_q()
    result = AttributeSet.objects.filter(q)
    assert len(result) == expected_subjects


@pytest.mark.django_db
def test_to_q_for_exclusive_study_and_no_prs():
    own_sfg = subject_filter_group_exclusive_study(is_exclusive=True)
    mommy.make(AttributeSet, data=dict(d1=1), _quantity=4)

    result = AttributeSet.objects.filter(own_sfg.to_q())
    assert len(result) == 4


@pytest.mark.django_db
def test_to_q_for_exclusive_study_and_pr_in_finished_study(attributesets):
    own_sfg = subject_filter_group_exclusive_study(is_exclusive=True)
    pr_for_exclusive_studies(attributesets=attributesets, is_finished=True, is_exclusive=False)

    result = AttributeSet.objects.filter(own_sfg.to_q())
    assert len(result) == 4


@pytest.mark.django_db
def test_to_q_for_exclusive_study_and_pr_in_unfinished_study(attributesets):
    own_sfg = subject_filter_group_exclusive_study(is_exclusive=True)
    pr_for_exclusive_studies(attributesets=attributesets, is_finished=False, is_exclusive=False)

    result = AttributeSet.objects.filter(own_sfg.to_q())
    assert len(result) == 3


@pytest.mark.django_db
def test_to_q_other_study_exclusive_and_finished(attributesets):
    own_sfg = subject_filter_group_exclusive_study(is_exclusive=False)
    pr_for_exclusive_studies(attributesets=attributesets, is_finished=True, is_exclusive=True)

    result = AttributeSet.objects.filter(own_sfg.to_q())
    assert len(result) == 4


@pytest.mark.django_db
def test_to_q_for_when_other_study_is_exclusive_and_unfinished(attributesets):
    own_sfg = subject_filter_group_exclusive_study(is_exclusive=False)
    pr_for_exclusive_studies(attributesets=attributesets, is_finished=False, is_exclusive=True)

    result = AttributeSet.objects.filter(own_sfg.to_q())
    assert len(result) == 3


@pytest.mark.django_db
def test_to_q_for_with_mixed_studies(attributesets):
    own_sfg = subject_filter_group_exclusive_study(is_exclusive=False)
    pr_for_exclusive_studies(attributesets=attributesets, is_finished=False, is_exclusive=False)
    pr_for_exclusive_studies(attributesets=attributesets, is_finished=True, is_exclusive=True)

    result = AttributeSet.objects.filter(own_sfg.to_q())
    assert len(result) == 4
