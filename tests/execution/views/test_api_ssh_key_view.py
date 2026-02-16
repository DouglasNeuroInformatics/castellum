# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.utils import timezone
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain
from castellum.pseudonyms.models import SSHKeyPair
from castellum.recruitment.models import Participation


@pytest.fixture
def ssh_key_url(study, domain, pseudonym):
    return (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )


@pytest.fixture
def domain(study):
    return baker.make(Domain, context=study)


@pytest.fixture
def pseudonym(subject, domain):
    return get_pseudonym(subject, domain.key)


@pytest.fixture
def participating(study, subject):
    return baker.make(
        Participation, study=study, subject=subject, status=Participation.PARTICIPATING
    )


def test_get_creates_key(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert 'public_key' in data
    assert data['public_key'].startswith('ssh-ed25519 ')
    assert data['algorithm'] == 'ed25519'
    assert 'created_at' in data

    # Verify key was stored
    assert SSHKeyPair.objects.filter(study=study, subject=subject).exists()
    key = SSHKeyPair.objects.get(study=study, subject=subject)
    assert key.private_key  # Private key should be stored


def test_get_returns_existing_key(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    # Pre-create a key
    existing_key = baker.make(
        SSHKeyPair,
        study=study,
        subject=subject,
        public_key='ssh-ed25519 AAAA... test@example',
        private_key='private-key-data',
    )

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert data['public_key'] == existing_key.public_key


def test_delete_shreds_key(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    baker.make(
        SSHKeyPair,
        study=study,
        subject=subject,
        public_key='ssh-ed25519 AAAA...',
        private_key='secret-private-key',
    )

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'shredded'
    assert 'shredded_at' in data

    # Verify private key is gone
    key = SSHKeyPair.objects.get(study=study, subject=subject)
    assert key.private_key == ''
    assert key.shredded_at is not None


def test_get_after_shred_returns_410(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    baker.make(
        SSHKeyPair,
        study=study,
        subject=subject,
        public_key='ssh-ed25519 AAAA...',
        private_key='',
        shredded_at=timezone.now(),
    )

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 410
    data = response.json()
    assert data['error'] == 'Key has been shredded'


def test_delete_already_shredded_returns_409(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    baker.make(
        SSHKeyPair,
        study=study,
        subject=subject,
        public_key='ssh-ed25519 AAAA...',
        private_key='',
        shredded_at=timezone.now(),
    )

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 409
    data = response.json()
    assert data['error'] == 'Key already shredded'


def test_delete_nonexistent_returns_404(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 404


def test_privacy_level_enforcement(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    subject.privacy_level = 2
    subject.save()

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 403


def test_participation_status_required(
    settings, client, conductor, study, subject, domain, pseudonym
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    # Create participation with non-invited status
    baker.make(
        Participation, study=study, subject=subject, status=Participation.NOT_CONTACTED
    )

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 404


def test_unrelated_domain_returns_404(
    settings, client, conductor, study, subject, participating
):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    # Create domain not attached to study
    unrelated_domain = baker.make(Domain)
    pseudonym = get_pseudonym(subject, unrelated_domain.key)

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{unrelated_domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 404


def test_authentication_required(settings, client, study, domain, pseudonym):
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    url = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response = client.get(url)

    assert response.status_code == 403


def test_returns_correct_key_for_study_subject_pair(
    settings, client, conductor, study, subject, domain, pseudonym, participating
):
    """Verify each study/subject pair gets its own unique key."""
    settings.CASTELLUM_SSH_KEYS_ENABLED = True

    # Create a second subject with its own participation and key
    from castellum.subjects.models import Subject
    subject2 = baker.make(Subject)
    baker.make(
        Participation, study=study, subject=subject2, status=Participation.PARTICIPATING
    )
    pseudonym2 = get_pseudonym(subject2, domain.key)

    # Create distinct keys for each subject
    key1 = baker.make(
        SSHKeyPair,
        study=study,
        subject=subject,
        public_key='ssh-ed25519 KEY_FOR_SUBJECT_1',
        private_key='private1',
    )
    key2 = baker.make(
        SSHKeyPair,
        study=study,
        subject=subject2,
        public_key='ssh-ed25519 KEY_FOR_SUBJECT_2',
        private_key='private2',
    )

    # Request key for subject 1
    url1 = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym}/ssh-key/'
    )
    response1 = client.get(url1, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')
    assert response1.status_code == 200
    assert response1.json()['public_key'] == 'ssh-ed25519 KEY_FOR_SUBJECT_1'

    # Request key for subject 2
    url2 = (
        f'/execution/api/studies/{study.pk}'
        f'/domains/{domain.key}/{pseudonym2}/ssh-key/'
    )
    response2 = client.get(url2, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')
    assert response2.status_code == 200
    assert response2.json()['public_key'] == 'ssh-ed25519 KEY_FOR_SUBJECT_2'
