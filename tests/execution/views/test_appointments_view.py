import datetime

import pytest
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.utils import timezone
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.castellum_auth.models import User
from castellum.recruitment.models import Participation
from castellum.studies.models import Resource
from castellum.studies.models import StudyMembership
from castellum.studies.models import StudySession


def test_appointment(client, member, participation):
    session = baker.make(StudySession, study=participation.study)

    participation.status = participation.INVITED
    participation.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/appointments/'.format(
        participation.study.pk, participation.pk
    )
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

    participation.status = participation.INVITED
    participation.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/appointments/'.format(
        participation.study.pk, participation.pk
    )
    response = client.post(url, {
        'status': 2,
    })
    assert response.status_code == 302
    assert not participation.appointment_set.exists()


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

    participation.status = participation.INVITED
    participation.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/appointments/'.format(
        participation.study.pk, participation.pk
    )
    response = client.post(url, {
        'status': 2,
        f'appointment-{session1.pk}_0': '2020-01-01',
        f'appointment-{session1.pk}_1': '12:00',
        f'appointment-{session2.pk}_0': '2020-01-01',
        f'appointment-{session2.pk}_1': time,
    })
    assert response.status_code == 302
    messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert 'Some appointments overlap' not in messages


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
    resource = baker.make(Resource, name='MRI')
    session = baker.make(
        StudySession, study=participation.study, duration=60, resources=[resource]
    )
    baker.make(
        Appointment,
        session=session,
        start=timezone.make_aware(timezone.datetime(2020, 1, 1, 12)),
        participation__study=participation.study,
        participation__status=Participation.INVITED,
    )

    participation.status = participation.INVITED
    participation.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/appointments/'.format(
        participation.study.pk, participation.pk
    )
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': time,
    })
    assert response.status_code == 302
    messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert 'Some appointments for MRI overlap' not in messages


def test_appointment_change_appointment_permission(client, member, participation):
    future = timezone.now() + datetime.timedelta(days=10000)
    user = baker.make(
        User, expiration_date=future, email='test@example.com', privacy_level=1
    )
    user.user_permissions.add(Permission.objects.get(codename='recruit'))
    StudyMembership.objects.create(user=user, study=participation.study)

    session = baker.make(StudySession, study=participation.study, duration=60)

    participation.status = participation.INVITED
    participation.save()

    url = f'/recruitment/{participation.study.pk}/{participation.pk}/appointments/'

    client.force_login(user)
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': '12:00',
    })
    assert response.status_code == 403
    assert not participation.appointment_set.exists()

    client.force_login(member)
    response = client.post(url, {
        'status': 2,
        f'appointment-{session.pk}_0': '2020-01-01',
        f'appointment-{session.pk}_1': '12:00',
    })
    assert response.status_code == 302
    assert participation.appointment_set.exists()
