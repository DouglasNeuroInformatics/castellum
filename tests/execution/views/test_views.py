import pytest
from model_bakery import baker

from castellum.recruitment.models import Appointment
from castellum.recruitment.models import Participation


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_study_detail_view(request, client, user_fixture, study_in_execution_status):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    url = '/execution/{}/'.format(study_in_execution_status.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_participation_detail_view_invited(
    request, client, user_fixture, subject, study_in_execution_status
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.INVITED,
        subject=subject,
    )

    url = '/execution/{}/{}/'.format(study_in_execution_status.pk, participation.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_participation_detail_view_unsuitable(
    request, client, subject, conductor, study_in_execution_status
):
    client.force_login(conductor)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.UNSUITABLE,
        subject=subject,
    )

    url = '/execution/{}/{}/'.format(study_in_execution_status.pk, participation.pk)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.smoketest
def test_resolve_view(client, member, study_in_execution_status, subject):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.INVITED,
        subject=subject,
    )

    url = '/execution/%i/resolve/' % study_in_execution_status.pk
    response = client.post(url, {
        'pseudonym': participation.pseudonym,
    })

    assert response.status_code == 302
    assert response.url == '/execution/%i/%i/' % (
        study_in_execution_status.pk, participation.pk
    )


@pytest.mark.smoketest
def test_update_contact_view(client, member, study_in_execution_status, subject):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.INVITED,
        subject=subject,
    )

    response = client.get('/execution/%i/%i/update-contact/' % (
        study_in_execution_status.pk, participation.pk
    ))

    assert response.status_code == 200


@pytest.mark.smoketest
def test_calendar_view(client, member, study_in_execution_status):
    client.force_login(member)
    response = client.get('/execution/%i/calendar/' % study_in_execution_status.pk)
    assert response.status_code == 200


def test_calendar_view_events(client, member, study_in_execution_status, subject):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.INVITED,
        subject=subject,
    )
    baker.make(
        Appointment,
        participation=participation,
        session__study=study_in_execution_status,
    )

    response = client.get('/execution/%i/calendar/?events' % study_in_execution_status.pk)

    assert response.status_code == 200

    data = response.json()
    assert 'events' in data
    assert len(data['events']) == 1
    assert data['events'][0]['url'] == '/execution/%i/%i/' % (
        study_in_execution_status.pk, participation.pk
    )


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'receptionist',
    pytest.param('conductor', marks=pytest.mark.xfail(strict=True)),
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_reception_view(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/execution/reception/')
    assert response.status_code == 200
