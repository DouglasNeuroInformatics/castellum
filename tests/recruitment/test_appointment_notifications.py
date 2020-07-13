from django.core import mail
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import pytest
from freezegun import freeze_time

from castellum.recruitment.views import ContactView


def dt(s):
    return timezone.make_aware(parse_datetime(s))


def get_view(rf, user, study, participation):
    view = ContactView()
    view.request = rf.get('/test/')
    view.request.user = user
    view.study = study
    view.object = participation
    return view


@pytest.mark.parametrize('start', [
    '2017-01-01 12:00',
    '2017-01-02 12:00',
])
def test_appointment_notifications(rf, user, member, study, participation, start):
    view = get_view(rf, user, study, participation)
    with freeze_time('2017-01-01'):
        view.send_appointment_notifications([
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
    rf, user, member, study, participation, start
):
    view = get_view(rf, user, study, participation)
    with freeze_time('2017-01-01'):
        view.send_appointment_notifications([
            (dt(start), None),
        ])
    assert len(mail.outbox) == 0


def test_appointment_notifications_no_change(rf, user, member, study, participation):
    view = get_view(rf, user, study, participation)
    view.send_appointment_notifications([])
    assert len(mail.outbox) == 0


def test_appointment_notifications_no_members(rf, user, study, participation):
    view = get_view(rf, user, study, participation)
    with freeze_time('2017-01-01'):
        view.send_appointment_notifications([
            (dt('2017-01-01 12:00'), dt('2017-01-01 13:00')),
        ])
    assert len(mail.outbox) == 0


def test_appointment_notifications_weekend(rf, user, member, study, participation):
    view = get_view(rf, user, study, participation)
    with freeze_time('2017-01-06'):
        view.send_appointment_notifications([
            # friday to monday
            (dt('2017-01-09 12:00'), dt('2017-01-09 13:00')),
        ])
    assert len(mail.outbox) == 1
