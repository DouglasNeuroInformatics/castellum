import pytest
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import ExecutionTag
from castellum.recruitment.models import Participation
from castellum.studies.models import StudySession


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_participation_list_view(
    request, client, user_fixture, study_in_execution_status
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    url = f'/execution/{study_in_execution_status.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_participation_list_view_appointment_count(
    client, member, subject, study_in_execution_status
):
    session = baker.make(StudySession, study=study_in_execution_status)
    baker.make(StudySession, study=study_in_execution_status)
    participation = baker.make(
        Participation,
        status=Participation.PARTICIPATING,
        subject=subject,
        study=study_in_execution_status,
    )
    baker.make(Appointment, participation=participation, session=session)

    client.force_login(member)
    url = f'/execution/{study_in_execution_status.pk}/'
    response = client.get(url)
    assert b'1/2' in response.content


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
        status=Participation.PARTICIPATING,
        subject=subject,
    )

    url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_participation_detail_view_excluded(
    request, client, subject, conductor, study_in_execution_status
):
    client.force_login(conductor)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.EXCLUDED,
        subject=subject,
    )

    url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 404


def test_participation_detail_view_tags(
    client, subject, conductor, study_in_execution_status
):
    client.force_login(conductor)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )
    tag = baker.make(ExecutionTag, name='test_tag', study=study_in_execution_status)
    participation.execution_tags.add(tag)
    url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 200
    assert b'test_tag' in response.content


@pytest.mark.smoketest
def test_resolve_view(client, member, study_in_execution_status, subject):
    client.force_login(member)

    domain = baker.make(Domain, context=study_in_execution_status)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )

    url = f'/execution/{study_in_execution_status.pk}/resolve/'

    response = client.get(url)
    assert b'<input type="hidden" name="domain"' in response.content

    pseudonym = get_pseudonym(subject, domain.key)

    response = client.post(url, {
        'domain': domain.key,
        'pseudonym': pseudonym,
    })

    assert response.status_code == 302
    expected_url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/'
    assert response.url == expected_url


def test_resolve_view_wrong_domain(client, member, study_in_execution_status, subject):
    client.force_login(member)

    domain1 = baker.make(Domain, context=study_in_execution_status)
    domain2 = baker.make(Domain, context=study_in_execution_status)

    baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )

    url = f'/execution/{study_in_execution_status.pk}/resolve/'

    response = client.get(url)
    assert b'<select name="domain"' in response.content

    response = client.post(url, {
        'domain': domain1.key,
        'pseudonym': get_pseudonym(subject, domain2.key),
    })

    assert response.status_code == 200


@pytest.mark.smoketest
def test_update_contact_view(client, member, study_in_execution_status, subject):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )

    url = (
        f'/execution/{study_in_execution_status.pk}'
        f'/{participation.pk}/update-contact/'
    )
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.smoketest
def test_calendar_view(client, member, study_in_execution_status):
    client.force_login(member)
    response = client.get(f'/execution/{study_in_execution_status.pk}/calendar/')
    assert response.status_code == 200


def test_calendar_view_events(client, member, study_in_execution_status, subject):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )
    baker.make(
        Appointment,
        participation=participation,
        session__study=study_in_execution_status,
    )

    response = client.get(f'/execution/{study_in_execution_status.pk}/calendar/?events')

    assert response.status_code == 200

    data = response.json()
    assert 'events' in data
    assert len(data['events']) == 1
    expected_url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/'
    assert data['events'][0]['url'] == expected_url


@pytest.mark.smoketest
def test_participation_update_view(client, member, study_in_execution_status, subject):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )
    url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/update/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
def test_participation_status_view(client, member, study_in_execution_status, subject):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )
    url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/status/'
    response = client.get(url)
    assert response.status_code == 200


def test_participation_status_view_post(
    client, member, study_in_execution_status, subject
):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )
    url = f'/execution/{study_in_execution_status.pk}/{participation.pk}/status/'
    response = client.post(url, {
        'status': str(Participation.PARTICIPATING_DROPPED_OUT)
    })
    participation.refresh_from_db()
    assert response.status_code == 302
    assert participation.status == Participation.PARTICIPATING_DROPPED_OUT


def test_participation_dropout_confirm_view_post(
    client, member, study_in_execution_status, subject
):
    client.force_login(member)

    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
        subject=subject,
    )
    url = (
        f'/execution/{study_in_execution_status.pk}/{participation.pk}/dropout/confirm/'
    )
    response = client.post(url)
    participation.refresh_from_db()
    assert response.status_code == 302
    assert participation.status == Participation.EXCLUDED_DROPPED_OUT


@pytest.mark.smoketest
def test_progress_view(client, member, study_in_execution_status):
    client.force_login(member)
    url = f'/execution/{study_in_execution_status.pk}/progress/'
    response = client.get(url)
    assert response.status_code == 200
