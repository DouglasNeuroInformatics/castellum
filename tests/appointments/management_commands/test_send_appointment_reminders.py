from django.core import mail
from django.utils import timezone

from freezegun import freeze_time
from model_bakery import baker

from castellum.appointments.management.commands.send_appointment_reminders import \
    send_appointment_reminders
from castellum.appointments.models import Appointment
from castellum.participations.models import Participation
from castellum.studies.models import StudySession


def test_send_appointment_reminders(contact, study_in_execution_status):
    contact.email = 'test@example.com'
    contact.save()
    participation = baker.make(
        Participation,
        subject=contact.subject,
        study=study_in_execution_status,
        status=Participation.INVITED,
    )
    session = baker.make(StudySession, study=study_in_execution_status)

    with freeze_time('1970-01-01 12:00'):
        baker.make(Appointment, session=session, participation=participation, start=timezone.now())
        reached_count, not_reached_count = send_appointment_reminders('https://example.com')

    assert reached_count == 1
    assert len(mail.outbox) == 1
