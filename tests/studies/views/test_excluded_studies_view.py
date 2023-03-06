import pytest


@pytest.mark.smoketest
def test_200(client, member, study):
    client.force_login(member)
    response = client.get(f'/studies/{study.pk}/recruitmentsettings/excluded-studies/')
    assert response.status_code == 200
