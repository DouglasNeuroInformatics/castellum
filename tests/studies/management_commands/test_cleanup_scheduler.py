from unittest.mock import patch

from freezegun import freeze_time
from model_bakery import baker

from castellum.studies.management.commands import cleanup_scheduler
from castellum.studies.models import Study
from castellum.studies.models import StudySession


def test_cleanup_scheduler(participation):
    cmd = cleanup_scheduler.Command()

    with freeze_time('1970-01-01'):
        participation.study.status = Study.FINISHED
        participation.study.save()
        session = baker.make(StudySession, study=participation.study, schedule_id='abc')
        assert session.domain  # create domain

    with freeze_time('1972-01-01'):
        with patch('castellum.utils.scheduler.delete_schedule') as mock:
            cmd.handle(dry_run=False, months=12, verbosity=0)
            assert mock.called

    session.refresh_from_db()
    assert session.schedule_id is None
    assert not session.domains.exists()


def test_too_new(participation):
    cmd = cleanup_scheduler.Command()

    with freeze_time('1970-01-01'):
        participation.study.status = Study.FINISHED
        participation.study.save()
        session = baker.make(StudySession, study=participation.study, schedule_id='abc')
        assert session.domain  # create domain

    with freeze_time('1970-02-01'):
        with patch('castellum.utils.scheduler.delete_schedule') as mock:
            cmd.handle(dry_run=False, months=12, verbosity=0)
            assert not mock.called

    session.refresh_from_db()
    assert session.schedule_id == 'abc'
    assert session.domains.exists()
