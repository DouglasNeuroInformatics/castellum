from freezegun import freeze_time
from model_bakery import baker

from castellum.subjects.forms import DataProtectionForm
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument


def test_consent_no_change(user, contact):
    initial = baker.make(Consent, subject=contact.subject, status=Consent.CONFIRMED)

    baker.make(ConsentDocument)
    form = DataProtectionForm(user=user, instance=contact.subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()
    form.save()

    assert contact.subject.consent.status == Consent.CONFIRMED
    assert contact.subject.consent.document == initial.document


def test_consent_create_document(user, contact):
    form = DataProtectionForm(user=user, instance=contact.subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()

    assert not ConsentDocument.objects.exists()
    form.save()
    assert ConsentDocument.objects.exists()


def test_consent_confirm_direct(user, contact):
    form = DataProtectionForm(user=user, instance=contact.subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()
    form.save()

    assert contact.subject.consent.status == Consent.CONFIRMED


def test_consent_confirm_from_waiting(user, contact):
    initial = baker.make(Consent, subject=contact.subject, status=Consent.WAITING)
    baker.make(ConsentDocument)

    form = DataProtectionForm(user=user, instance=contact.subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()
    form.save()

    assert contact.subject.consent.status == Consent.CONFIRMED
    assert contact.subject.consent.document == initial.document


def test_consent_withdraw(user, contact):
    baker.make(Consent, subject=contact.subject, status=Consent.CONFIRMED)

    form = DataProtectionForm(user=user, instance=contact.subject, data={
        'privacy_level': 0,
    })
    assert form.is_valid()
    form.save()

    assert not Consent.objects.exists()


def test_consent_update(user, contact):
    baker.make(Consent, subject=contact.subject, status=Consent.CONFIRMED)

    new_document = baker.make(ConsentDocument)
    form = DataProtectionForm(user=user, instance=contact.subject, data={
        'privacy_level': 0,
        'consent_status': Consent.WAITING,
    })
    assert form.is_valid()
    form.save()

    assert contact.subject.consent.status == Consent.WAITING
    assert contact.subject.consent.document == new_document


def test_consent_renew_waiting(user, contact):
    with freeze_time('1990-01-01 12:00:00'):
        baker.make(Consent, subject=contact.subject, status=Consent.WAITING)

    with freeze_time('2000-01-01 12:00:00'):
        new_document = baker.make(ConsentDocument)
        form = DataProtectionForm(user=user, instance=contact.subject, data={
            'privacy_level': 0,
            'consent_status': Consent.WAITING,
        })
        assert form.is_valid()
        form.save()

    assert contact.subject.consent.status == Consent.WAITING
    assert contact.subject.consent.document == new_document


def test_consent_confirm_from_invalid(user, contact):
    initial_document = baker.make(ConsentDocument, is_valid=False)
    baker.make(
        Consent, subject=contact.subject, status=Consent.CONFIRMED, document=initial_document
    )

    new_document = baker.make(ConsentDocument)
    form = DataProtectionForm(user=user, instance=contact.subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()
    form.save()

    assert contact.subject.consent.status == Consent.CONFIRMED
    assert contact.subject.consent.document == new_document
