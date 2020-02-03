import pytest


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
