from unittest.mock import patch

from model_bakery import baker

from castellum.participations.models import Participation
from castellum.studies.models import StudySession
from castellum.utils import scheduler


@patch.object(scheduler, 'delete')
def test_scheduler_delete_token_on_uninvite(delete, settings, study):
    settings.SCHEDULER_URL = 'http://example.com'
    baker.make(StudySession, study=study, schedule_id=1)
    participation = baker.make(Participation, study=study, status=Participation.INVITED)
    participation.status = Participation.UNSUITABLE
    participation.save()
    assert delete.called


@patch.object(scheduler, 'delete')
def test_scheduler_delete_token_on_delete(delete, settings, study):
    settings.SCHEDULER_URL = 'http://example.com'
    baker.make(StudySession, study=study, schedule_id=1)
    participation = baker.make(Participation, study=study)
    participation.delete()
    assert delete.called
