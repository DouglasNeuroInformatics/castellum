import pytest
from model_bakery import baker

from castellum.recruitment.models.recruitment import ParticipationRequest
from castellum.studies.models import StudyMembership


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'study_conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_study_detail_view(request, client, user_fixture, study_in_execution_status):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    baker.make(StudyMembership, user=user, study=study_in_execution_status)

    url = '/execution/{}/'.format(study_in_execution_status.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'study_conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_participation_request_detail_view_invited(
    request, client, user_fixture, contact, study_in_execution_status
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    participationrequest = baker.make(
        ParticipationRequest,
        study=study_in_execution_status,
        status=ParticipationRequest.INVITED,
        subject=contact.subject,
    )
    baker.make(StudyMembership, user=user, study=study_in_execution_status)

    url = '/execution/{}/{}/'.format(study_in_execution_status.pk, participationrequest.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_participation_request_detail_view_unsuitable(
    request, client, contact, study_conductor, study_in_execution_status
):
    client.force_login(study_conductor)

    participationrequest = baker.make(
        ParticipationRequest,
        study=study_in_execution_status,
        status=ParticipationRequest.UNSUITABLE,
        subject=contact.subject,
    )
    baker.make(StudyMembership, user=study_conductor, study=study_in_execution_status)

    url = '/execution/{}/{}/'.format(study_in_execution_status.pk, participationrequest.pk)
    response = client.get(url)
    assert response.status_code == 404
