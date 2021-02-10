import pytest


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_studymembers_200(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get(f'/studies/{study.pk}/members/')
    assert response.status_code == 200
