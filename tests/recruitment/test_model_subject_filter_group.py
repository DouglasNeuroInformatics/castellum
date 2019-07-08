from itertools import cycle

import pytest
from model_mommy import mommy

from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest


"""
- create five studies (1-5)
- create one subject filter group for study 1
- create 4 subjects with attribute_sets
- subject 1 participates in study 2
- subject 2 participates in studies 2 and 3
- subject 3 participates in studies 2, 3 and 4
- subject 4 participates in studies 2, 3, 4 and 5
"""


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
def test_to_q_with_no_excluding_studies(subject_filter_group, participation_requests):
    q = subject_filter_group.to_q()
    result = AttributeSet.objects.filter(q)
    assert len(result) == 4


@pytest.mark.django_db
@pytest.mark.parametrize("excluding_study_idx,expected_subjects", [
    (1, 0),
    (2, 1),
    (3, 2),
    (4, 3),
])
def test_to_q_with_one_excluding_study(excluding_study_idx, expected_subjects,
                                       five_studies, subject_filter_group, participation_requests):
    excluding_study = five_studies[excluding_study_idx]
    subject_filter_group.excluded_studies.add(excluding_study)
    subject_filter_group.save()

    q = subject_filter_group.to_q()
    result = AttributeSet.objects.filter(q)
    assert len(result) == expected_subjects


@pytest.mark.django_db
@pytest.mark.parametrize("excluding_study_idx", [1, 2, 3, 4])
def test_to_q_when_subjects_are_unsuitable_for_other_studies(excluding_study_idx,
                                                             five_studies, subject_filter_group,
                                                             participation_requests):
    unsuitable = ParticipationRequest.UNSUITABLE
    ParticipationRequest.objects.filter(study__in=five_studies).update(status=unsuitable)

    excluding_study = five_studies[excluding_study_idx]
    subject_filter_group.excluded_studies.add(excluding_study)
    subject_filter_group.save()

    q = subject_filter_group.to_q()
    result = AttributeSet.objects.filter(q)
    assert len(result) == 4
