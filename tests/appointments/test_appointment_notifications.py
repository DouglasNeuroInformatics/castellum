from django.core import mail
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import pytest
from freezegun import freeze_time

from castellum.appointments.helpers import send_appointment_notifications


def dt(s):
    return timezone.make_aware(parse_datetime(s))


@pytest.mark.parametrize('start', [
    '2017-01-01 12:00',
    '2017-01-02 12:00',
])
def test_appointment_notifications(conductor, participation, start):
    with freeze_time('2017-01-01'):
        send_appointment_notifications(
            participation,
            (dt(start), None),
            'http://example.com',
        )
    assert len(mail.outbox) == 1


@pytest.mark.parametrize('start', [
    '2016-01-01 12:00',
    '2016-12-31 12:00',
    '2017-01-03 12:00',
    '2018-01-01 12:00',
])
def test_appointment_notifications_no_relevant_change(conductor, participation, start):
    with freeze_time('2017-01-01'):
        send_appointment_notifications(
            participation,
            (dt(start), None),
            'http://example.com',
        )
    assert len(mail.outbox) == 0


def test_appointment_notifications_weekend(conductor, participation):
    with freeze_time('2017-01-06'):
        send_appointment_notifications(
            participation,
            (dt('2017-01-09 12:00'), dt('2017-01-09 13:00')),  # friday to monday
            'http://example.com',
        )
    assert len(mail.outbox) == 1


def test_appointment_notifications_no_members(participation):
    with freeze_time('2017-01-01'):
        send_appointment_notifications(
            participation,
            (dt('2017-01-01 12:00'), None),
            'http://example.com',
        )
    assert len(mail.outbox) == 0


def test_appointment_notifications_cc(user, conductor, participation):
    with freeze_time('2017-01-01'):
        send_appointment_notifications(
            participation,
            (dt('2017-01-01 12:00'), None),
            'http://example.com',
            user=user,
        )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].cc == [user.email]


def test_no_appointment_notifications_if_only_conductor(conductor, participation):
    with freeze_time('2017-01-01'):
        send_appointment_notifications(
            participation,
            (dt('2017-01-01 12:00'), None),
            'http://example.com',
            user=conductor,
        )
    assert len(mail.outbox) == 0
