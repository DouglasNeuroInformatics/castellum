import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.data_protection import helpers
from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument
from castellum.subjects.models import Subject


def test_get_no_legal_basis(subject):
    actual = helpers.get_no_legal_basis()
    assert not subject in actual


def test_get_no_legal_basis_legal_representatives(subject):
    ward = baker.make(Contact)
    ward.legal_representatives.add(subject.contact)

    actual = helpers.get_no_legal_basis()

    assert subject not in actual


@pytest.mark.django_db
def test_get_no_legal_basis_study_consent_none():
    assert helpers.get_no_legal_basis().count() == 0
    with freeze_time('1970-01-01'):
        contact = baker.make(Contact)
        subject = contact.subject

    assert helpers.get_no_legal_basis().count() == 1


@pytest.mark.django_db
def test_get_no_legal_basis_study_consent_ignored():
    with freeze_time('1970-01-01'):
        contact = baker.make(Contact)
        subject_no_legal_basis = contact.subject
    study = baker.make(Study, status=Study.FINISHED)
    baker.make(Participation, subject=subject_no_legal_basis, study=study)
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
    document = baker.make(ConsentDocument)
    baker.make(Consent, subject=subject, document=document)
    assert subject.has_consent

    actual = helpers.get_no_legal_basis()

    assert subject not in actual


def test_get_no_legal_basis_consent_deceased(subject):
    subject.deceased = True
    subject.save()

    document = baker.make(ConsentDocument)
    baker.make(Consent, subject=subject, document=document)

    actual = helpers.get_no_legal_basis()

    assert subject in actual
