from django.utils import timezone
from freezegun import freeze_time
from model_bakery import baker

from castellum.appointments.management.commands.send_appointment_reminders import (
    send_appointment_reminders,
)
from castellum.appointments.models import Appointment
from castellum.recruitment.models import Participation
from castellum.studies.models import StudySession


def test_send_appointment_reminders_first(
    mailoutbox, contact, study_in_execution_status,
):
    contact.email = 'test@example.com'
    contact.save()
    participation = baker.make(
        Participation,
        subject=contact.subject,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
    )
    session = baker.make(
        StudySession, study=study_in_execution_status, first_reminder_days=3
    )

    with freeze_time('1970-01-01 12:00'):
        appointment = baker.make(
            Appointment,
            session=session,
            participation=participation,
            start=timezone.now(),
        )
        reached_count, not_reached_count = (
            send_appointment_reminders('https://example.com')
        )

    assert reached_count == 1
    assert len(mailoutbox) == 1

    appointment.refresh_from_db()
    assert appointment.first_reminder_sent is True


def test_send_appointment_reminders_second(
    mailoutbox,
    contact,
    study_in_execution_status,
):
    contact.email = 'test@example.com'
    contact.save()
    participation = baker.make(
        Participation,
        subject=contact.subject,
        study=study_in_execution_status,
        status=Participation.PARTICIPATING,
    )
    session = baker.make(
        StudySession, study=study_in_execution_status, second_reminder_days=3
    )

    with freeze_time('1970-01-01 12:00'):
        appointment = baker.make(
            Appointment,
            session=session,
            participation=participation,
            start=timezone.now(),
            first_reminder_sent=True,
        )
        reached_count, not_reached_count = (
            send_appointment_reminders('https://example.com')
        )

    assert reached_count == 1
    assert len(mailoutbox) == 1

    appointment.refresh_from_db()
    assert appointment.second_reminder_sent is True
