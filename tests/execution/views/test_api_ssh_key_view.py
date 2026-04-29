from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.pseudonyms.models import KeyPair
from castellum.pseudonyms.models import Pseudonym


def test_get_ssh_keys(db):
    pseudonym = baker.make(Pseudonym)
    key_pair = KeyPair(
        pseudonym=pseudonym,
        private_key=(
            b'\x9ec&\xf6\xed\xf6\xdfG\xf9\xf9\xb5:\r\xfbN\x94'
            b'\x85dd\xb9\xf9\x0f\x0c\xe23\x84\xc4\xa2u2\xc5\x9f'
        ),
    )

    assert key_pair.get_ssh_private_key().startswith(
        '-----BEGIN OPENSSH PRIVATE KEY-----'
    )
    assert key_pair.get_ssh_public_key() == (
        'ssh-ed25519 '
        'AAAAC3NzaC1lZDI1NTE5AAAAIMZUyYVzxYY8nlnbnpUr5PvxD7z0jBsgEg15EWHjQOet'
    )


def test_get_creates_key(client, conductor, study, subject):
    domain = baker.make(Domain, context=study)
    pseudonym = baker.make(Pseudonym, domain=domain, subject=subject)

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/{pseudonym}/ssh-key/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert 'public_key' in data
    assert data['public_key'].startswith('ssh-ed25519 ')

    assert KeyPair.objects.filter(pseudonym=pseudonym).exists()


def test_404_on_invalid_pseudonym(client, conductor, study, subject):
    domain = baker.make(Domain, context=study)
    pseudonym = 'X'

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/{pseudonym}/ssh-key/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')

    assert response.status_code == 404


def test_404_on_deleted_subject(client, conductor, study, subject):
    domain = baker.make(Domain, context=study)
    pseudonym = baker.make(Pseudonym, domain=domain, subject=subject)

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/{pseudonym}/ssh-key/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')
    assert response.status_code == 200
    assert KeyPair.objects.exists()

    subject.delete()

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/{pseudonym}/ssh-key/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {conductor.token}')
    assert response.status_code == 404
    assert not KeyPair.objects.exists()
