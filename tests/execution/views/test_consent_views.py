from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

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
        'file': SimpleUploadedFile('foo.pdf', b'dummy'),
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
