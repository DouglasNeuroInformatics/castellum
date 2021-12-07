from unittest.mock import patch

from django.utils import timezone

from model_bakery import baker

from castellum.appointments.helpers import fetch_scheduler_appointments
from castellum.appointments.models import Appointment
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.studies.models import StudySession


def test_fetch_scheduler_appointments(participation):
    participation.status = participation.INVITED
    participation.save()

    session = baker.make(StudySession, study=participation.study, schedule_id='test_scheduler')
    pseudonym = get_pseudonym(participation.subject, session.domain)
    scheduler_data = {pseudonym: timezone.now()}

    with patch('castellum.utils.scheduler.get_bulk', return_value=scheduler_data) as mock:
        fetch_scheduler_appointments(participation.study, 'http://example.com')
        mock.assert_called_once_with('test_scheduler')

    appointment = Appointment.objects.first()
    assert appointment
    assert appointment.start == scheduler_data[pseudonym]
