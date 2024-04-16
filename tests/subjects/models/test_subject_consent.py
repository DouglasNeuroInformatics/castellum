import pytest
from model_bakery import baker

from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument


@pytest.mark.django_db
def test_unknown_consent_no_info(subject):
    assert subject.unknown_consent is True


@pytest.mark.django_db
def test_unknown_consent_rejected(subject):
    baker.make(Consent, subject=subject)
    assert subject.unknown_consent is False


@pytest.mark.django_db
def test_unknown_consent_accepted(subject):
    document = baker.make(ConsentDocument)
    baker.make(Consent, document=document, subject=subject)
    assert subject.unknown_consent is False


@pytest.mark.django_db
def test_unknown_consent_deprecated_document(subject):
    document = baker.make(ConsentDocument, is_deprecated=True)
    baker.make(Consent, document=document, subject=subject)
    assert subject.unknown_consent is False


@pytest.mark.django_db
def test_unknown_consent_invalid_document(subject):
    document = baker.make(ConsentDocument, is_valid=False)
    baker.make(Consent, document=document, subject=subject)
    assert subject.unknown_consent is True


@pytest.mark.django_db
def test_has_consent_no_info(subject):
    assert subject.has_consent is False


@pytest.mark.django_db
def test_has_consent_rejected(subject):
    baker.make(Consent, subject=subject)
    assert subject.has_consent is False


@pytest.mark.django_db
def test_has_consent_accepted(subject):
    document = baker.make(ConsentDocument)
    baker.make(Consent, document=document, subject=subject)
    assert subject.has_consent is True


@pytest.mark.django_db
def test_has_consent_deprecated_document(subject):
    document = baker.make(ConsentDocument, is_deprecated=True)
    baker.make(Consent, document=document, subject=subject)
    assert subject.has_consent is True


@pytest.mark.django_db
def test_has_consent_invalid_document(subject):
    document = baker.make(ConsentDocument, is_valid=False)
    baker.make(Consent, document=document, subject=subject)
    assert subject.has_consent is False
