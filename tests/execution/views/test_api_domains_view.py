from model_bakery import baker

from castellum.pseudonyms.models import Domain


def test_apidomainsview(client, conductor, study_in_execution_status):
    baker.make(Domain, context=study_in_execution_status)
    baker.make(Domain, context=study_in_execution_status)

    url = f'/execution/api/studies/{study_in_execution_status.pk}/domains/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['domains']) == 2


def test_no_general_domains(client, conductor, study_in_execution_status):
    domain = baker.make(Domain)
    study_in_execution_status.general_domains.add(domain)
    conductor.general_domains.add(domain)

    url = f'/execution/api/studies/{study_in_execution_status.pk}/domains/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {conductor.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['domains']) == 0


def test_permission(client, recruiter, study_in_execution_status):
    url = f'/execution/api/studies/{study_in_execution_status.pk}/domains/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {recruiter.token}')
    assert response.status_code == 403


def test_only_token_auth(client, conductor, study_in_execution_status):
    client.force_login(conductor)
    url = f'/execution/api/studies/{study_in_execution_status.pk}/domains/'
    response = client.get(url)
    assert response.status_code == 403
