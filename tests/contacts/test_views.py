import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_detail_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_create_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/create/form/'
    response = client.get(url)
    assert response.status_code == 200


def test_create_with_parameter_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/create/form/?first_name=test'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_update_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/update/'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_update_with_parameter_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/update/?first_name=test'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_requestcreate_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/request/'
    response = client.get(url)
    assert response.status_code == 200


def test_requestcreate_with_parameters_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/request/?first_name=test&last_name=test&date_of_birth=2000-02-02'
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
    url = '/subjects/{}/export/'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200
