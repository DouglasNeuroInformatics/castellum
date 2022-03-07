import datetime

import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.subjects.models import Consent


@pytest.mark.django_db
def test_has_consent_from_before_full_age():
    contact = baker.make(Contact, date_of_birth=datetime.date(2000, 1, 1))

    with freeze_time('2014-01-01'):
        baker.make(
            Consent, status=Consent.CONFIRMED, subject=contact.subject, underage_when_given=True
        )

    with freeze_time('2018-01-01'):
        assert contact.subject.has_consent_from_before_full_age


@pytest.mark.django_db
def test_has_consent_from_before_full_age_not_full_age():
    contact = baker.make(Contact, date_of_birth=datetime.date(2010, 1, 1))

    with freeze_time('2014-01-01'):
        baker.make(
            Consent, status=Consent.CONFIRMED, subject=contact.subject, underage_when_given=True
        )

    with freeze_time('2018-01-01'):
        assert not contact.subject.has_consent_from_before_full_age


@pytest.mark.django_db
def test_has_consent_from_before_full_age_newer_consent():
    contact = baker.make(Contact, date_of_birth=datetime.date(2000, 1, 1))

    with freeze_time('2017-01-01'):
        baker.make(
            Consent, status=Consent.CONFIRMED, subject=contact.subject, underage_when_given=False
        )

    with freeze_time('2018-01-01'):
        assert not contact.subject.has_consent_from_before_full_age
