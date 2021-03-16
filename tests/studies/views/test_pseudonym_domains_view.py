import pytest


@pytest.mark.smoketest
def test_200(client, study, member):
    client.force_login(member)
    response = client.get('/studies/{}/domains/'.format(study.pk))
    assert response.status_code == 200


def test_add(client, study, member):
    client.force_login(member)
    response = client.post('/studies/{}/domains/'.format(study.pk))
    assert response.status_code == 302
    assert study.domains.count() == 2
