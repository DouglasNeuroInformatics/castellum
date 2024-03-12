from django.utils import timezone
from django.utils.dateparse import parse_datetime

from castellum.appointments.helpers import send_appointment_notifications
from castellum.appointments.models import AppointmentState


def dt(s):
    return timezone.make_aware(parse_datetime(s))


def test_appointment_notifications(mailoutbox, conductor, participation):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
    )
    assert len(mailoutbox) == 1


def test_appointment_notifications_no_members(mailoutbox, participation):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
    )
    assert len(mailoutbox) == 0


def test_appointment_notifications_cc(mailoutbox, user, conductor, participation):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
        user=user,
    )
    assert len(mailoutbox) == 1
    assert mailoutbox[0].cc == [user.email]


def test_no_appointment_notifications_if_only_conductor(
    mailoutbox,
    conductor,
    participation,
):
    send_appointment_notifications(
        participation,
        (AppointmentState(dt('2017-01-01 12:00'), set()), None),
        'http://example.com',
        user=conductor,
    )
    assert len(mailoutbox) == 0
