import pytest


def test_index_200(client, user):
    client.force_login(user)
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_studies_availablea(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/')
    assert b'Studies' in response.content
