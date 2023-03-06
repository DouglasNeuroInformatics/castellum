import pytest
from django.core import mail
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from freezegun import freeze_time

from castellum.appointments.helpers import change_is_urgent
from castellum.appointments.helpers import send_appointment_notifications
from castellum.appointments.models import AppointmentState


def dt(s):
    return timezone.make_aware(parse_datetime(s))


@pytest.mark.parametrize('start', [
    '2017-01-01 12:00',
    '2017-01-02 12:00',
])
def test_change_is_urgent(start):
    with freeze_time('2017-01-01'):
        assert change_is_urgent((AppointmentState(dt(start), set()), None))


@pytest.mark.parametrize('start', [
    '2016-01-01 12:00',
    '2016-12-31 12:00',
    '2017-01-03 12:00',
    '2018-01-01 12:00',
])
def test_change_is_not_urgent(start):
    with freeze_time('2017-01-01'):
        assert not change_is_urgent((AppointmentState(dt(start), set()), None))


def test_change_is_urgent_weekend(user, member, participation):
    with freeze_time('2017-01-06'):
        # friday to monday
        assert change_is_urgent((
            AppointmentState(dt('2017-01-09 12:00'), set()),
            AppointmentState(dt('2017-01-09 13:00'), set()),
        ))


def test_appointment_notifications(conductor, participation):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
    )
    assert len(mail.outbox) == 1


def test_appointment_notifications_no_members(participation):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
    )
    assert len(mail.outbox) == 0


def test_appointment_notifications_cc(user, conductor, participation):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
        user=user,
    )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].cc == [user.email]


def test_no_appointment_notifications_if_only_conductor(conductor, participation):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
        user=conductor,
    )
    assert len(mail.outbox) == 0
