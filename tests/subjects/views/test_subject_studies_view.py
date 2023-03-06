import pytest


def test_200(client, user, subject):
    client.force_login(user)
    response = client.get(f'/subjects/{subject.pk}/participations/recruit/')
    assert response.status_code == 200
    assert b'No matching studies found' in response.content


def test_200_with_study(client, member, subject, study_in_execution_status):
    client.force_login(member)
    response = client.get(f'/subjects/{subject.pk}/participations/recruit/')
    assert response.status_code == 200
    assert b'No attributes provided' not in response.content
    assert b'No matching studies found' not in response.content


@pytest.mark.smoketest
def test_finished_200(client, member, subject):
    client.force_login(member)
    response = client.get(f'/subjects/{subject.pk}/participations/add/')
    assert response.status_code == 200
