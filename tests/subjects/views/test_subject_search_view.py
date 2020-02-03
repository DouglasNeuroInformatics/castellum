import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
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
