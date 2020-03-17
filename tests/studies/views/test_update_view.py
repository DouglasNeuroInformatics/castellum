import pytest

from castellum.studies.models import Study


@pytest.mark.smoketest
def test_200(client, member, study):
    client.force_login(member)
    response = client.get('/studies/{}/update/'.format(study.pk))
    assert response.status_code == 200


def test_readonly_get(client, member, study):
    study.status = Study.FINISHED
    study.save()

    client.force_login(member)
    response = client.get('/studies/{}/update/'.format(study.pk))

    assert response.status_code == 200
    assert b'readonly' in response.content


def test_readonly_post(client, member, study):
    study.status = Study.FINISHED
    study.save()

    client.force_login(member)
    response = client.post('/studies/{}/update/'.format(study.pk))

    assert response.status_code == 400
