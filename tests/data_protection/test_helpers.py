from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.data_protection import helpers
from castellum.recruitment.models import Participation
from castellum.subjects.models import Consent


def test_get_no_legal_basis(subject):
    actual = helpers.get_no_legal_basis()

    assert subject in actual


def test_get_no_legal_basis_legal_representatives(subject):
    ward = baker.make(Contact)
    ward.legal_representatives.add(subject.contact)

    actual = helpers.get_no_legal_basis()

    assert subject not in actual


def test_get_no_legal_basis_participation(subject):
    baker.make(Participation, subject=subject)

    actual = helpers.get_no_legal_basis()

    assert subject not in actual


def test_get_no_legal_basis_consent(subject):
    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    actual = helpers.get_no_legal_basis()

    assert subject not in actual


def test_get_no_legal_basis_consent_deceased(subject):
    subject.deceased = True
    subject.save()

    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    actual = helpers.get_no_legal_basis()

    assert subject in actual
