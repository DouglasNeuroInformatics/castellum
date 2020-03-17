import pytest


@pytest.mark.smoketest
def test_index_200(client, user):
    client.force_login(user)
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_studies_tile(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/')
    assert b'Studies' in response.content


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_subjects_tile(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/')
    assert b'Subjects' in response.content


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_data_protection_tile(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/')
    assert b'Data protection' in response.content
