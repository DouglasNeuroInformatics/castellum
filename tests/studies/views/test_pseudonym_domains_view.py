import pytest
from model_bakery import baker

from castellum.pseudonyms.models import Domain


@pytest.mark.smoketest
def test_200(client, study, member):
    client.force_login(member)
    response = client.get('/studies/{}/domains/'.format(study.pk))
    assert response.status_code == 200


def test_add(client, study, member):
    client.force_login(member)
    response = client.post('/studies/{}/domains/'.format(study.pk), {
        'action': 'add',
    })
    assert response.status_code == 302
    assert study.domains.count() == 1


def test_name(client, study, member):
    client.force_login(member)
    domain = baker.make(Domain, context=study)
    response = client.post('/studies/{}/domains/'.format(study.pk), {
        'action': 'name',
        'domain': domain.key,
        'name': 'foo',
    })
    assert response.status_code == 302
    domain.refresh_from_db()
    assert domain.name == 'foo'


def test_delete(client, study, member):
    client.force_login(member)
    domain = study.domains.create()
    response = client.post('/studies/{}/domains/{}/'.format(study.pk, domain.key))
    assert response.status_code == 302
    assert study.domains.count() == 0
