import datetime

from django.core import mail
from freezegun import freeze_time

from castellum.studies.management.commands.notify_pseudonyms_delete import Command


def test_notify_pseudonyms_delete(study, member):
    with freeze_time('1970-01-01 12:00'):
        study.name = 'test'
        study.pseudonyms_delete_date = datetime.date.today()
        study.save()
        study.domains.create()

        cmd = Command()
        cmd.handle()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == '[Castellum] [test] Pseudonyms should be deleted'
    assert mail.outbox[0].to == [member.email]


def test_notify_pseudonyms_delete_no_pseudonyms(study, member):
    with freeze_time('1970-01-01 12:00'):
        study.name = 'test'
        study.pseudonyms_delete_date = datetime.date.today()
        study.save()

        cmd = Command()
        cmd.handle()

    assert len(mail.outbox) == 0
