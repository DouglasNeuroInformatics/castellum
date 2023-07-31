from django.core import mail
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from castellum.appointments.helpers import send_appointment_notifications
from castellum.appointments.models import AppointmentState


def dt(s):
    return timezone.make_aware(parse_datetime(s))


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
