import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
])
def test_search_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/subjects/')
    assert 200 == response.status_code


def test_search_with_parameters_200(client, user):
    client.force_login(user)
    url = '/subjects/?first_name=Test&last_name=Test'
    response = client.get(url)
    assert 200 == response.status_code


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_create_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/'
    response = client.post(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
])
def test_detail_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_contact_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/contact/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_export_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/export/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200
