from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.recruitment.models import Participation


def test_apipseudonymsview(client, conductor, study, subject):
    domain = baker.make(Domain, context=study)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.PARTICIPATING
    )

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['pseudonyms']) == 1


def test_participation_status(client, conductor, study, subject):
    domain = baker.make(Domain, context=study)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.NOT_CONTACTED
    )

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['pseudonyms']) == 0


def test_privacy_level(client, conductor, study, subject):
    subject.privacy_level = 2
    subject.save()

    domain = baker.make(Domain, context=study)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.PARTICIPATING
    )

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['pseudonyms']) == 1


def test_unrelated_domain(client, conductor, study, subject):
    domain = baker.make(Domain)
    baker.make(
        Participation, study=study, subject=subject, status=Participation.PARTICIPATING
    )

    url = f'/execution/api/studies/{study.pk}/domains/{domain.key}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 404
