import pytest


@pytest.mark.smoketest
def test_200(client, conductor, study_in_execution_status):
    client.force_login(conductor)
    url = '/execution/{}/?export'.format(study_in_execution_status.pk)
    response = client.get(url)
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/zip'
