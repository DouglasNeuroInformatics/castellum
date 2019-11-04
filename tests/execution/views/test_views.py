import pytest
from model_mommy import mommy

from castellum.recruitment.models.recruitment import ParticipationRequest
from castellum.studies.models import StudyMembership


@pytest.mark.parametrize('user_fixture', [
    'study_conductor',
    'study_coordinator',
    'recruiter',
    'subject_manager',
    'data_protection_officer',
])
def test_study_list_view(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    response = client.get('/execution/')
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    'study_conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_officer',
])
def test_study_detail_view(request, client, user_fixture, study_in_execution_status):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    mommy.make(StudyMembership, user=user, study=study_in_execution_status)

    url = '/execution/{}/'.format(study_in_execution_status.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    'study_conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_officer',
])
def test_participation_request_detail_view_invited(
    request, client, user_fixture, contact, study_in_execution_status
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    participationrequest = mommy.make(
        ParticipationRequest,
        study=study_in_execution_status,
        status=ParticipationRequest.INVITED,
        subject=contact.subject,
    )
    mommy.make(StudyMembership, user=user, study=study_in_execution_status)

    url = '/execution/{}/{}/'.format(study_in_execution_status.pk, participationrequest.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_participation_request_detail_view_unsuitable(
    request, client, contact, study_conductor, study_in_execution_status
):
    client.force_login(study_conductor)

    participationrequest = mommy.make(
        ParticipationRequest,
        study=study_in_execution_status,
        status=ParticipationRequest.UNSUITABLE,
        subject=contact.subject,
    )
    mommy.make(StudyMembership, user=study_conductor, study=study_in_execution_status)

    url = '/execution/{}/{}/'.format(study_in_execution_status.pk, participationrequest.pk)
    response = client.get(url)
    assert response.status_code == 404
