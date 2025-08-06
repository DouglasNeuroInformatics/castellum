from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from castellum.recruitment.models import Participation
from castellum.recruitment.models import ParticipationConsent


def test_list(client, member, invited):
    client.force_login(member)
    url = f'/execution/{invited.study.pk}/{invited.pk}/consent/'
    response = client.get(url)
    assert response.status_code == 200


def test_create_get(client, member, invited):
    client.force_login(member)
    url = f'/execution/{invited.study.pk}/{invited.pk}/consent/add/'
    response = client.get(url)
    assert response.status_code == 200


def test_create_post(client, member, invited):
    client.force_login(member)
    url = f'/execution/{invited.study.pk}/{invited.pk}/consent/add/'
    response = client.post(url, {
        'file': SimpleUploadedFile('foo.pdf', b'%PDF-dummy'),
    })
    assert response.status_code == 302
    assert invited.participationconsent_set.exists()


def test_delete_get(client, member, invited):
    client.force_login(member)
    consent = baker.make(ParticipationConsent, participation=invited)
    url = f'/execution/{invited.study.pk}/{invited.pk}/consent/{consent.pk}/delete/'
    response = client.get(url)
    assert response.status_code == 200
    assert invited.participationconsent_set.exists()


def test_delete_post(client, member, invited):
    client.force_login(member)
    consent = baker.make(ParticipationConsent, participation=invited)
    url = f'/execution/{invited.study.pk}/{invited.pk}/consent/{consent.pk}/delete/'
    response = client.post(url)
    assert response.status_code == 302
    assert not invited.participationconsent_set.exists()


def test_media_get(client, member, invited):
    client.force_login(member)
    url = f'/execution/{invited.study.pk}/{invited.pk}/consent/add/'
    response = client.post(url, {
        'file': SimpleUploadedFile('foo.pdf', b'%PDF-dummy'),
    })
    consent = invited.participationconsent_set.first()

    response = client.get(consent.file.url)
    assert response.status_code == 200


def test_media_other_participant(client, member, invited):
    client.force_login(member)
    url = f'/execution/{invited.study.pk}/{invited.pk}/consent/add/'
    response = client.post(url, {
        'file': SimpleUploadedFile('foo.pdf', b'%PDF-dummy'),
    })
    consent = invited.participationconsent_set.first()

    other = baker.make(
        Participation,
        study=invited.study,
        status=Participation.PARTICIPATING,
    )
    response = client.get(consent.file.url.replace(
        f'{invited.study.pk}/{invited.pk}',
        f'{other.study.pk}/{other.pk}',
    ))
    assert response.status_code == 404
