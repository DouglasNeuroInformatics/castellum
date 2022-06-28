from freezegun import freeze_time
from model_bakery import baker

from castellum.subjects.forms import DataProtectionForm
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument
from castellum.subjects.models import Subject


def test_consent_no_change(user, subject):
    document = baker.make(ConsentDocument)
    initial = baker.make(Consent, subject=subject, document=document)

    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': document.pk,
    })
    assert form.is_valid()
    form.save()

    assert subject.consent.document == initial.document


def test_consent_create_document(user, subject):
    assert not ConsentDocument.objects.exists()
    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': 1,
    })
    assert form.is_valid()
    form.save()
    assert ConsentDocument.objects.exists()


def test_consent_confirm_from_waiting(user, subject):
    document = baker.make(ConsentDocument)
    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
        'consent_status': document.pk,
    })
    assert form.is_valid()
    form.save()

    assert ConsentDocument.objects.filter(consent__subject=subject).exists()
    assert subject.consent.document == document


def test_consent_withdraw(user, subject):
    document = baker.make(ConsentDocument)
    consent = baker.make(Consent, subject=subject, document=document)

    form = DataProtectionForm(user=user, instance=subject, data={
        'privacy_level': 0,
    })
    assert form.is_valid()
    form.save()

    subject = Subject.objects.get(pk=consent.subject.pk)
    assert not subject.has_consent
    assert not subject.consent.document


def test_consent_renew_waiting(user, subject):
    with freeze_time('1990-01-01 12:00:00'):
        baker.make(Consent, subject=subject)

    with freeze_time('2000-01-01 12:00:00'):
        document = baker.make(ConsentDocument)
        form = DataProtectionForm(user=user, instance=subject, data={
            'privacy_level': 0,
            'consent_status': document.pk,
        })
        assert form.is_valid()
        form.save()

    assert subject.consent.document == document
