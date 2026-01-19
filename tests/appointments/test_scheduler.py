from unittest.mock import patch

from model_bakery import baker

from castellum.appointments.forms import AppointmentsForm
from castellum.recruitment.models import Participation
from castellum.studies.models import StudySession
from castellum.utils import scheduler


@patch.object(scheduler, 'delete')
def test_scheduler_delete_token_on_uninvite(delete, settings, study):
    settings.SCHEDULER_URL = 'http://example.com'
    session = baker.make(StudySession, study=study, schedule_id='1dd7sdtsg')
    participation = baker.make(
        Participation, study=study, status=Participation.PARTICIPATING
    )
    form = AppointmentsForm(instance=participation)
    form.get_invitation_url(session)

    participation.status = Participation.EXCLUDED
    participation.save()
    assert delete.called


@patch.object(scheduler, 'delete')
def test_scheduler_delete_token_on_delete(delete, settings, study):
    settings.SCHEDULER_URL = 'http://example.com'
    session = baker.make(StudySession, study=study, schedule_id='7sdvsd81')
    participation = baker.make(
        Participation, study=study, status=Participation.PARTICIPATING
    )
    form = AppointmentsForm(instance=participation)
    form.get_invitation_url(session)

    participation.delete()
    assert delete.called
