import pytest


def test_200_without_attributeset(client, user, contact):
    client.force_login(user)
    response = client.get('/subjects/{}/participations/add/'.format(contact.subject.slug))
    assert response.status_code == 200
    assert b'No attributes provided' in response.content


def test_200_with_attributeset(client, user, contact, attributeset):
    client.force_login(user)
    response = client.get('/subjects/{}/participations/add/'.format(contact.subject.slug))
    assert response.status_code == 200
    assert b'No matching studies found' in response.content


def test_200_with_attributeset_and_study(
    client, member, contact, attributeset, study_in_execution_status
):
    client.force_login(member)
    response = client.get('/subjects/{}/participations/add/'.format(contact.subject.slug))
    assert response.status_code == 200
    assert b'No attributes provided' not in response.content
    assert b'No matching studies found' not in response.content


@pytest.mark.smoketest
def test_finished_200(client, member, contact):
    client.force_login(member)
    response = client.get('/subjects/{}/participations/add-finished/'.format(contact.subject.slug))
    assert response.status_code == 200
