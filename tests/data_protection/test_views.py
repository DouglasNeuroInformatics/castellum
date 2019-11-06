from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.data_protection.views import DataProtectionView
from castellum.recruitment.models import ParticipationRequest


def test_iter_orphans(db):
    contact = mommy.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    view = DataProtectionView()
    actual, missing = view.get_orphans()

    assert contact.subject in actual
    assert missing == 0


def test_iter_orphans_guardians(db):
    contact = mommy.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    ward = mommy.make(Contact)
    ward.guardians.add(contact)

    view = DataProtectionView()
    actual, missing = view.get_orphans()

    assert contact.subject not in actual
    assert missing == 0


def test_iter_orphans_participation(db):
    contact = mommy.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    mommy.make(ParticipationRequest, subject=contact.subject)

    view = DataProtectionView()
    actual, missing = view.get_orphans()

    assert contact.subject not in actual
    assert missing == 0
