from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.data_protection import helpers
from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
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


def test_get_should_delete_participations(subject):
    study1 = baker.make(Study, status=Study.FINISHED)
    baker.make(Domain, context=study1)
    baker.make(Participation, subject=subject, study=study1)

    study2 = baker.make(Study, status=Study.EXECUTION)
    baker.make(Participation, subject=subject, study=study2)

    assert helpers.get_should_delete_participations().count() == 0

    study3 = baker.make(Study, status=Study.FINISHED)
    baker.make(Participation, subject=subject, study=study3)

    assert helpers.get_should_delete_participations().count() == 1

    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)

    assert helpers.get_should_delete_participations().count() == 0
