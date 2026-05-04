import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.pseudonyms.models import Pseudonym
from castellum.recruitment.models import Participation
from castellum.recruitment.models import ReliabilityEntry
from castellum.subjects.models import Consent
from castellum.subjects.models import Subject


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_officer',
])
def test_merge(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    target = baker.make(Subject)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})

    assert response.status_code == 302
    assert not Subject.objects.filter(pk=subject.pk).exists()


def test_merge_participation_moved(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    participation = baker.make(Participation, subject=subject)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})

    participation.refresh_from_db()
    assert response.status_code == 302
    assert participation.subject == target


def test_merge_participation_conflict(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    participation = baker.make(Participation, subject=subject)
    baker.make(Participation, subject=target, study=participation.study)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})

    assert response.status_code == 200


def test_merge_pseudonym_moved(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    pseudonym = baker.make(Pseudonym, subject=subject)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})

    pseudonym.refresh_from_db()
    assert response.status_code == 302
    assert pseudonym.subject == target


def test_merge_pseudonym_conflict(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    pseudonym = baker.make(Pseudonym, subject=subject)
    baker.make(Pseudonym, subject=target, domain=pseudonym.domain)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})

    assert response.status_code == 200


def test_merge_reliabilityentry_moved(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    entry = baker.make(ReliabilityEntry, subject=subject)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})
    assert response.status_code == 302

    merged_entry = ReliabilityEntry.objects.get(subject=target, study=entry.study)
    assert merged_entry.subject == target


def test_merge_reliabilityentry_merged(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    entry = baker.make(ReliabilityEntry, subject=subject, was_reliable=False)
    baker.make(ReliabilityEntry, subject=target, study=entry.study, was_reliable=True)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})
    assert response.status_code == 302

    merged_entry = ReliabilityEntry.objects.get(subject=target, study=entry.study)
    assert merged_entry.was_reliable is False


def test_merge_consent_moved(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    consent = baker.make(Consent, subject=subject)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})

    consent.refresh_from_db()
    assert response.status_code == 302
    assert consent.subject == target


def test_merge_consent_merged(client, user, subject):
    client.force_login(user)

    target = baker.make(Subject)
    with freeze_time('2019-01-01'):
        consent = baker.make(Consent, subject=subject)
    with freeze_time('2018-01-01'):
        baker.make(Consent, subject=target)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.pk})

    consent.refresh_from_db()
    assert response.status_code == 302
    assert consent.subject == target


def test_merge_legal_rep_of_copies(client, user, subject):
    client.force_login(user)

    child = baker.make(Contact)
    child.legal_representatives.add(subject.contact)

    target = baker.make(Contact)
    url = f'/subjects/{subject.pk}/merge/'
    response = client.post(url, {'target': target.subject_uuid})

    child.refresh_from_db()
    assert response.status_code == 302
    assert child.legal_representatives.get() == target
