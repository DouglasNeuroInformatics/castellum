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


def test_get_no_legal_basis_study_consent_none(subject):
    assert helpers.get_no_legal_basis().count() == 1


def test_get_no_legal_basis_study_consent_ignored(subject):
    study = baker.make(Study, status=Study.FINISHED)
    baker.make(Participation, subject=subject, study=study)
    assert helpers.get_no_legal_basis().count() == 1


def test_get_no_legal_basis_study_consent_pseudonym(subject):
    study = baker.make(Study, status=Study.FINISHED)
    baker.make(Domain, context=study)
    baker.make(Participation, subject=subject, study=study)
    assert helpers.get_no_legal_basis().count() == 0


def test_get_no_legal_basis_study_consent_study_status(subject):
    study = baker.make(Study, status=Study.EXECUTION)
    baker.make(Participation, subject=subject, study=study)
    assert helpers.get_no_legal_basis().count() == 0


def test_get_no_legal_basis_study_consent_news_interest(subject):
    study = baker.make(Study, status=Study.FINISHED)
    baker.make(Participation, subject=subject, study=study, news_interest=Participation.VIA_EMAIL)
    assert helpers.get_no_legal_basis().count() == 0


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
