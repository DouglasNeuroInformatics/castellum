import datetime

from freezegun import freeze_time

from castellum.studies.management.commands.notify_sessions_end import Command


def test_notify_sessions_end(study, conductor, mailoutbox):
    with freeze_time('1970-01-01 12:00'):
        study.name = 'test'
        study.sessions_end = datetime.date.today()
        study.save()

        cmd = Command()
        cmd.handle()

    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == '[Castellum] [test] Sessions ended'
    assert mailoutbox[0].to == [conductor.email]
