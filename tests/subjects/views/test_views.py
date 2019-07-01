import pytest

from django.urls import reverse


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
])
def test_status_code_200_for_contact_index_view(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get(reverse('subjects:index'))
    assert 200 == response.status_code


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
def test_status_code_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/create/?first_name=Test&last_name=Test&date_of_birth=1982-02-03'
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_create_400(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/create/'
    response = client.post(url)
    assert response.status_code == 400


def test_create_with_parameter_400(client, user):
    client.force_login(user)
    url = '/subjects/create/?first_name=test'
    response = client.post(url)
    assert response.status_code == 400


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


def test_contact_with_parameter_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/contact/?first_name=test'.format(contact.subject.pk)
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
