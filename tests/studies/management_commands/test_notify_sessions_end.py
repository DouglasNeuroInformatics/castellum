import datetime

from django.core import mail

from freezegun import freeze_time

from castellum.studies.management.commands.notify_sessions_end import Command


def test_notify_sessions_end(study, conductor):
    with freeze_time("1970-01-01 12:00"):
        study.name = 'test'
        study.sessions_end = datetime.date.today()
        study.save()

        cmd = Command()
        cmd.handle()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == '[Castellum] [test] Sessions ended'
    assert mail.outbox[0].to == [conductor.email]
