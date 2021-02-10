import datetime

from django.contrib.auth.models import Permission
from django.utils import timezone

import pytest
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.castellum_auth.models import User
from castellum.recruitment.models import Participation
from castellum.studies.models import Resource
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership
from castellum.studies.models import StudySession


@pytest.mark.smoketest
def test_200(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/3/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_wrong_study_is_provided(client, member, participation, study):
    client.force_login(member)
    url = f'/recruitment/{study.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_study_in_edit_status(client, member, participation):
    participation.study.status = Study.EDIT
    participation.study.save()

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 404


def test_back_to_list(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 200
    assert b'Back to list' in response.content


def test_back_to_subject(client, member, participation):
    participation.status = 1
    participation.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/?context=subjects:participation-list'.format(
        participation.study.pk, participation.pk
    )
    response = client.get(url)
    assert response.status_code == 200
    assert b'Back to subject' in response.content


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    client.post(url, {'status': Participation.UNSUITABLE})
    participation = Participation.objects.get()
    assert participation.updated_at.strftime('%Y-%m-%d') == '2018-01-01'


def test_appointment(client, member, participation):
    session = baker.make(StudySession, study=participation.study)

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': '12:00',
    })
    assert response.status_code == 302

    appointment = participation.appointment_set.first()
    assert appointment.session == session
    assert appointment.participation == participation


def test_appointment_delete(client, member, participation):
    session = baker.make(StudySession, study=participation.study)
    baker.make(
        Appointment,
        session=session,
        participation=participation,
    )

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.post(url, {
        'status': 2,
    })
    assert response.status_code == 302
    assert not participation.appointment_set.exists()


def test_warning_on_appointment_deletion(client, member, participation):
    participation.status = Participation.INVITED
    participation.save()

    session = baker.make(StudySession, study=participation.study, schedule_id=123)
    baker.make(
        Appointment,
        session=session,
        participation=participation,
    )

    client.force_login(member)

    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    warning = b'Scheduler appointments for this participation have been deleted.'

    response = client.post(url, {
        'status': Participation.INVITED,
    }, follow=True)
    assert warning not in response.content

    response = client.post(url, {
        'status': Participation.UNSUITABLE,
    }, follow=True)
    assert warning in response.content


@pytest.mark.parametrize('time', (
    '10:30',
    '11:00',
    pytest.param('11:30', marks=pytest.mark.xfail(strict=True)),
    pytest.param('12:00', marks=pytest.mark.xfail(strict=True)),
    pytest.param('12:30', marks=pytest.mark.xfail(strict=True)),
    '13:00',
    '13:30',
))
def test_appointment_overlap(client, member, participation, time):
    session1 = baker.make(StudySession, study=participation.study, duration=60)
    session2 = baker.make(StudySession, study=participation.study, duration=60)

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.post(url, {
        'status': 2,
        f'appointment-{session1.pk}_0': '2020-01-01',
        f'appointment-{session1.pk}_1': '12:00',
        f'appointment-{session2.pk}_0': '2020-01-01',
        f'appointment-{session2.pk}_1': time,
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
def test_appointment_resource_overlap(client, member, participation, time):
    resource = baker.make(Resource)
    session = baker.make(
        StudySession, study=participation.study, duration=60, resource=resource
    )
    baker.make(
        Appointment,
        session=session,
        start=timezone.make_aware(timezone.datetime(2020, 1, 1, 12)),
        participation__study=participation.study,
        participation__status=Participation.INVITED,
    )

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': time,
    })
    assert response.status_code == 302


def test_appointment_resource_overlap_ignore_not_invited(client, member, participation):
    resource = baker.make(Resource)
    session = baker.make(
        StudySession, study=participation.study, duration=60, resource=resource
    )
    baker.make(
        Appointment,
        session=session,
        start=timezone.make_aware(timezone.datetime(2020, 1, 1, 12)),
        participation__study=participation.study,
        participation__status=Participation.UNSUITABLE,
    )

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': '12:00',
    })
    assert response.status_code == 302


def test_appointment_change_appointment_permission(client, member, participation):
    future = timezone.now() + datetime.timedelta(days=10000)
    user = baker.make(User, expiration_date=future, email='test@example.com')
    user.user_permissions.add(Permission.objects.get(codename='privacy_level_1'))
    user.user_permissions.add(Permission.objects.get(codename='recruit'))
    StudyMembership.objects.create(user=user, study=participation.study)

    session = baker.make(StudySession, study=participation.study, duration=60)

    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'

    client.force_login(user)
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': '12:00',
    })
    assert response.status_code == 302
    assert not participation.appointment_set.exists()

    client.force_login(member)
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': '12:00',
    })
    assert response.status_code == 302
    assert participation.appointment_set.exists()
