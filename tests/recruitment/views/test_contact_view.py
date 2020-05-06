from django.utils import timezone

import pytest
from model_bakery import baker

from castellum.recruitment.models import Appointment
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision
from castellum.studies.models import Resource
from castellum.studies.models import Study
from castellum.studies.models import StudySession


@pytest.mark.smoketest
def test_200(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/3/{}/'.format(participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_wrong_study_is_provided(client, member, participation_request, study):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_study_in_edit_status(client, member, participation_request):
    participation_request.study.status = Study.EDIT
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_post_redirect(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(participation_request.study.pk)


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    client.post(url, {'status': ParticipationRequest.UNSUITABLE})
    participation_request = ParticipationRequest.objects.get()
    assert participation_request.updated_at.strftime('%Y-%m-%d') == '2018-01-01'


def test_create_revision_on_update(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    client.post(url, {'status': 2})

    assert ParticipationRequestRevision.objects.count() == 2


def test_post_redirect_from_contacts(client, member, participation_request):
    participation_request.status = 1
    participation_request.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/?context=subjects:participation-list'.format(
        participation_request.study.pk, participation_request.pk
    )
    response = client.post(url, {'status': 2})
    assert response.status_code == 302
    assert response.url.startswith('/subjects/')


def test_appointment(client, member, participation_request):
    session = baker.make(StudySession, study=participation_request.study)

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(
        participation_request.study.pk, participation_request.pk
    )
    response = client.post(url, {
        'status': 2,
        'appointment-%i_0' % session.pk: '2020-01-01',
        'appointment-%i_1' % session.pk: '12:00',
    })
    assert response.status_code == 302

    appointment = participation_request.appointment_set.first()
    assert appointment.session == session
    assert appointment.participant == participation_request


def test_appointment_delete(client, member, participation_request):
    session = baker.make(StudySession, study=participation_request.study)
    baker.make(
        Appointment,
        session=session,
        participant=participation_request,
    )

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(
        participation_request.study.pk, participation_request.pk
    )
    response = client.post(url, {
        'status': 2,
    })
    assert response.status_code == 302
    assert not participation_request.appointment_set.exists()


@pytest.mark.parametrize('time', (
    '10:30',
    '11:00',
    pytest.param('11:30', marks=pytest.mark.xfail(strict=True)),
    pytest.param('12:00', marks=pytest.mark.xfail(strict=True)),
    pytest.param('12:30', marks=pytest.mark.xfail(strict=True)),
    '13:00',
    '13:30',
))
def test_appointment_overlap(client, member, participation_request, time):
    session1 = baker.make(StudySession, study=participation_request.study, duration=60)
    session2 = baker.make(StudySession, study=participation_request.study, duration=60)

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(
        participation_request.study.pk, participation_request.pk
    )
    response = client.post(url, {
        'status': 2,
        'appointment-%i_0' % session1.pk: '2020-01-01',
        'appointment-%i_1' % session1.pk: '12:00',
        'appointment-%i_0' % session2.pk: '2020-01-01',
        'appointment-%i_1' % session2.pk: time,
    })
    assert response.status_code == 302


@pytest.mark.parametrize('time', (
    '10:30',
    '11:00',
    pytest.param('11:30', marks=pytest.mark.xfail(strict=True)),
    pytest.param('12:00', marks=pytest.mark.xfail(strict=True)),
    pytest.param('12:30', marks=pytest.mark.xfail(strict=True)),
    '13:00',
    '13:30',
))
def test_appointment_resource_overlap(client, member, participation_request, time):
    resource = baker.make(Resource)
    session = baker.make(
        StudySession, study=participation_request.study, duration=60, resource=resource
    )
    baker.make(
        Appointment,
        session=session,
        start=timezone.make_aware(timezone.datetime(2020, 1, 1, 12)),
        participant__study=participation_request.study,
        participant__status=ParticipationRequest.INVITED,
    )

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(
        participation_request.study.pk, participation_request.pk
    )
    response = client.post(url, {
        'status': 2,
        'appointment-%i_0' % session.pk: '2020-01-01',
        'appointment-%i_1' % session.pk: time,
    })
    assert response.status_code == 302


def test_appointment_resource_overlap_ignore_not_invited(client, member, participation_request):
    resource = baker.make(Resource)
    session = baker.make(
        StudySession, study=participation_request.study, duration=60, resource=resource
    )
    baker.make(
        Appointment,
        session=session,
        start=timezone.make_aware(timezone.datetime(2020, 1, 1, 12)),
        participant__study=participation_request.study,
        participant__status=ParticipationRequest.UNSUITABLE,
    )

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(
        participation_request.study.pk, participation_request.pk
    )
    response = client.post(url, {
        'status': 2,
        'appointment-%i_0' % session.pk: '2020-01-01',
        'appointment-%i_1' % session.pk: '12:00',
    })
    assert response.status_code == 302
