import datetime

import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.subjects.management.commands.delete_consent_on_full_age import Command
from castellum.subjects.models import Consent


@pytest.mark.django_db
def test_delete_consent_on_full_age():
    with freeze_time('2017-01-10'):
        contact = baker.make(Contact, date_of_birth=datetime.date(2000, 1, 1))
        baker.make(Consent, status=Consent.CONFIRMED, subject=contact.subject)

    with freeze_time('2018-01-10'):
        cmd = Command()
        cmd.handle()

    consent = Consent.objects.get(subject=contact.subject)
    assert consent.status == Consent.EXPIRED


@pytest.mark.django_db
def test_delete_consent_on_full_age_not_full_age():
    with freeze_time('2017-01-10'):
        contact = baker.make(Contact, date_of_birth=datetime.date(2002, 1, 1))
        baker.make(Consent, status=Consent.CONFIRMED, subject=contact.subject)

    with freeze_time('2018-01-10'):
        cmd = Command()
        cmd.handle()

    consent = Consent.objects.get(subject=contact.subject)
    assert consent.status != Consent.EXPIRED


@pytest.mark.django_db
def test_delete_consent_on_full_age_newer_consent():
    with freeze_time('2019-01-10'):
        contact = baker.make(Contact, date_of_birth=datetime.date(2000, 1, 1))
        baker.make(Consent, status=Consent.CONFIRMED, subject=contact.subject)

    with freeze_time('2018-01-10'):
        cmd = Command()
        cmd.handle()

    consent = Consent.objects.get(subject=contact.subject)
    assert consent.status != Consent.EXPIRED
