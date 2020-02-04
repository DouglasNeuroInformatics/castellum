import pytest

from castellum.contacts.models import Contact


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/subjects/')
    assert response.status_code == 200
    assert b'create-tab' not in response.content


def test_with_parameters_200(client, user):
    client.force_login(user)
    url = '/subjects/?search=foo+bar'
    response = client.get(url)
    assert response.status_code == 200
    assert b'create-tab' in response.content


def test_no_create_tab_on_incomplete_name(client, user):
    client.force_login(user)
    url = '/subjects/?search=foo+foo@example.com'
    response = client.get(url)
    assert response.status_code == 200
    assert b'create-tab' not in response.content


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_create(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/?search=foo+bar+foo@example.com'
    response = client.post(url, {'privacy_level': 0})
    assert response.status_code == 302
    qs = Contact.objects.filter(first_name='foo', last_name='bar', email='foo@example.com')
    assert qs.exists()
    assert qs.get().subject.privacy_level == 0


def test_create_only_email(client, user):
    client.force_login(user)
    url = '/subjects/?search=foo@example.com'
    response = client.post(url, {'privacy_level': 0})
    assert response.status_code == 200


def test_create_no_search(client, user):
    client.force_login(user)
    url = '/subjects/'
    response = client.post(url, {'privacy_level': 0})
    assert response.status_code == 200
