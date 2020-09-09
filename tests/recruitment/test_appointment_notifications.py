from django.core import mail
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import pytest
from freezegun import freeze_time

from castellum.recruitment.mixins import send_appointment_notifications


def dt(s):
    return timezone.make_aware(parse_datetime(s))


@pytest.mark.parametrize('start', [
    '2017-01-01 12:00',
    '2017-01-02 12:00',
])
def test_appointment_notifications(rf, user, member, participation, start):
    request = rf.get('/test/')
    request.user = user
    with freeze_time('2017-01-01'):
        send_appointment_notifications(request, participation, [
            (dt(start), None),
        ])
    assert len(mail.outbox) == 1


@pytest.mark.parametrize('start', [
    '2016-01-01 12:00',
    '2016-12-31 12:00',
    '2017-01-03 12:00',
    '2018-01-01 12:00',
])
def test_appointment_notifications_no_relevant_change(
    rf, user, member, participation, start
):
    request = rf.get('/test/')
    request.user = user
    with freeze_time('2017-01-01'):
        send_appointment_notifications(request, participation, [
            (dt(start), None),
        ])
    assert len(mail.outbox) == 0


def test_appointment_notifications_no_change(rf, user, member, participation):
    request = rf.get('/test/')
    request.user = user
    send_appointment_notifications(request, participation, [])
    assert len(mail.outbox) == 0


def test_appointment_notifications_no_members(rf, user, participation):
    request = rf.get('/test/')
    request.user = user
    with freeze_time('2017-01-01'):
        send_appointment_notifications(request, participation, [
            (dt('2017-01-01 12:00'), dt('2017-01-01 13:00')),
        ])
    assert len(mail.outbox) == 0


def test_appointment_notifications_weekend(rf, user, member, participation):
    request = rf.get('/test/')
    request.user = user
    with freeze_time('2017-01-06'):
        send_appointment_notifications(request, participation, [
            # friday to monday
            (dt('2017-01-09 12:00'), dt('2017-01-09 13:00')),
        ])
    assert len(mail.outbox) == 1
