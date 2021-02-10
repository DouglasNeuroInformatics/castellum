from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.data_protection import helpers
from castellum.participations.models import Participation
from castellum.subjects.models import Consent


def test_get_no_legal_basis(subject):
    actual, missing = helpers.get_no_legal_basis(10)

    assert subject in actual
    assert missing == 0


def test_get_no_legal_basis_guardians(subject):
    ward = baker.make(Contact)
    ward.guardians.add(subject.contact)

    actual, missing = helpers.get_no_legal_basis(10)

    assert subject not in actual
    assert missing == 0


def test_get_no_legal_basis_participation(subject):
    baker.make(Participation, subject=subject)

    actual, missing = helpers.get_no_legal_basis(10)

    assert subject not in actual
    assert missing == 0


def test_get_no_legal_basis_consent(subject):
    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    actual, missing = helpers.get_no_legal_basis(10)

    assert subject not in actual
    assert missing == 0


def test_get_no_legal_basis_consent_deceased(subject):
    subject.deceased = True
    subject.save()

    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    actual, missing = helpers.get_no_legal_basis(10)

    assert subject in actual
    assert missing == 0
