from freezegun import freeze_time
from model_bakery import baker

from castellum.subjects.forms import DataProtectionForm
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument


def test_consent_no_change(user, subject):
    initial = baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    baker.make(ConsentDocument)
    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()
    form.save()

    assert subject.consent.status == Consent.CONFIRMED
    assert subject.consent.document == initial.document


def test_consent_create_document(user, subject):
    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()

    assert not ConsentDocument.objects.exists()
    form.save()
    assert ConsentDocument.objects.exists()


def test_consent_confirm_direct(user, subject):
    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()
    form.save()

    assert subject.consent.status == Consent.CONFIRMED


def test_consent_confirm_from_waiting(user, subject):
    initial = baker.make(Consent, subject=subject, status=Consent.WAITING)
    baker.make(ConsentDocument)

    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': Consent.CONFIRMED,
    })
    assert form.is_valid()
    form.save()

    assert subject.consent.status == Consent.CONFIRMED
    assert subject.consent.document == initial.document


def test_consent_withdraw(user, subject):
    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
    })
    assert form.is_valid()
    form.save()

    assert not Consent.objects.exists()


def test_consent_update(user, subject):
    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    new_document = baker.make(ConsentDocument)
    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': Consent.WAITING,
    })
    assert form.is_valid()
    form.save()

    assert subject.consent.status == Consent.WAITING
    assert subject.consent.document == new_document


def test_consent_renew_waiting(user, subject):
    with freeze_time('1990-01-01 12:00:00'):
        baker.make(Consent, subject=subject, status=Consent.WAITING)

    with freeze_time('2000-01-01 12:00:00'):
        new_document = baker.make(ConsentDocument)
        form = DataProtectionForm(user=user, instance=subject, data={
            'privacy_level': 0,
            'consent_status': Consent.WAITING,
        })
        assert form.is_valid()
        form.save()

    assert subject.consent.status == Consent.WAITING
    assert subject.consent.document == new_document
