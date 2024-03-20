from model_bakery import baker

from castellum.pseudonyms.models import Domain


def test_apidomainsview(client, conductor, study):
    baker.make(Domain, context=study)
    baker.make(Domain, context=study)

    url = f'/execution/api/studies/{study.pk}/domains/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['domains']) == 2


def test_no_general_domains(client, conductor, study):
    domain = baker.make(Domain)
    study.general_domains.add(domain)
    conductor.general_domains.add(domain)

    url = f'/execution/api/studies/{study.pk}/domains/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['domains']) == 0


def test_permission(client, recruiter, study):
    url = f'/execution/api/studies/{study.pk}/domains/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {recruiter.token}')
    assert response.status_code == 403


def test_only_token_auth(client, conductor, study):
    client.force_login(conductor)
    url = f'/execution/api/studies/{study.pk}/domains/'
    response = client.get(url)
    assert response.status_code == 403
