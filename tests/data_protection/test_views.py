import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.data_protection.views import DataProtectionView
from castellum.recruitment.models import ParticipationRequest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_officer',
])
def test_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/data-protection/')
    assert response.status_code == 200


def test_get_orphans(db):
    contact = mommy.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    view = DataProtectionView()
    actual, missing = view.get_orphans()

    assert contact.subject in actual
    assert missing == 0


def test_get_orphans_guardians(db):
    contact = mommy.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    ward = mommy.make(Contact)
    ward.guardians.add(contact)

    view = DataProtectionView()
    actual, missing = view.get_orphans()

    assert contact.subject not in actual
    assert missing == 0


def test_get_orphans_participation(db):
    contact = mommy.make(Contact)
    contact.subject.no_recruitment = True
    contact.subject.save()

    mommy.make(ParticipationRequest, subject=contact.subject)

    view = DataProtectionView()
    actual, missing = view.get_orphans()

    assert contact.subject not in actual
    assert missing == 0
