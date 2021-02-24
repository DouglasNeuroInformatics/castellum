import pytest


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'receptionist',
    pytest.param('conductor', marks=pytest.mark.xfail(strict=True)),
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_reception_view(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/appointments/reception/')
    assert response.status_code == 200
