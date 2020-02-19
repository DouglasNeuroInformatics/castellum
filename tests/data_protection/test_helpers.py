from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.data_protection import helpers
from castellum.recruitment.models import ParticipationRequest


def test_get_orphans(db):
    contact = baker.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    actual, missing = helpers.get_orphans(10)

    assert contact.subject in actual
    assert missing == 0


def test_get_orphans_guardians(db):
    contact = baker.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    ward = baker.make(Contact)
    ward.guardians.add(contact)

    actual, missing = helpers.get_orphans(10)

    assert contact.subject not in actual
    assert missing == 0


def test_get_orphans_participation(db):
    contact = baker.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    baker.make(ParticipationRequest, subject=contact.subject)

    actual, missing = helpers.get_orphans(10)

    assert contact.subject not in actual
    assert missing == 0
