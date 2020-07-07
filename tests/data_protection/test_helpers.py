from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.data_protection import helpers
from castellum.recruitment.models import Participation


def test_get_no_legal_basis(db):
    contact = baker.make(Contact)

    actual, missing = helpers.get_no_legal_basis(10)

    assert contact.subject in actual
    assert missing == 0


def test_get_no_legal_basis_guardians(db):
    contact = baker.make(Contact)

    ward = baker.make(Contact)
    ward.guardians.add(contact)

    actual, missing = helpers.get_no_legal_basis(10)

    assert contact.subject not in actual
    assert missing == 0


def test_get_no_legal_basis_participation(db):
    contact = baker.make(Contact)

    baker.make(Participation, subject=contact.subject)

    actual, missing = helpers.get_no_legal_basis(10)

    assert contact.subject not in actual
    assert missing == 0
