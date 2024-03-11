import datetime

import pytest
from django.core import mail
from django.core.management.base import CommandError
from freezegun import freeze_time
from model_bakery import baker

from castellum.subjects.management.commands.notify_on_full_age import Command
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument


def test_missing_settings(settings):
    settings.CASTELLUM_FULL_AGE_MAIL_SUBJECT = None
    settings.CASTELLUM_FULL_AGE_MAIL_BODY = None
    cmd = Command()
    with pytest.raises(CommandError):
        cmd.handle(verbosity=0)


@pytest.mark.parametrize('date,before1,before2,after1,after2,mails', [
    ('2015-01-01', False, False, False, False, 0),
    ('2016-01-01', False, False, False, False, 0),
    ('2016-02-01', False, False, True, False, 1),
    ('2016-03-01', False, False, True, False, 1),
    ('2017-09-01', True, False, True, False, 0),
    ('2017-10-01', True, False, True, True, 1),
    ('2017-11-01', True, False, True, True, 1),
    ('2020-01-01', False, False, True, True, 2),
])
def test_command(
    settings, mailoutbox, subject, date, before1, before2, after1, after2, mails
):
    settings.CASTELLUM_FULL_AGE_MAIL_SUBJECT = 'subject'
    settings.CASTELLUM_FULL_AGE_MAIL_BODY = 'body'

    subject.contact.date_of_birth = datetime.date(2000, 1, 1)
    subject.contact.email = 'foo@example.com'
    subject.contact.save()

    consent = baker.make(
        Consent,
        subject=subject,
        document=baker.make(ConsentDocument),
        underage_when_given=True,
        full_age_notified_1=before1,
        full_age_notified_2=before2,
    )

    cmd = Command()
    with freeze_time(date):
        cmd.handle(verbosity=0)

    consent.refresh_from_db()
    assert consent.full_age_notified_1 is after1
    assert consent.full_age_notified_2 is after2
    assert len(mail.outbox) == mails
