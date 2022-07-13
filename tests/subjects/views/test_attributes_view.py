import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_update_200(request, client, user_fixture, subject, attribute_description):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/attributes/'.format(subject.uuid)
    response = client.get(url)
    assert response.status_code == 200
    assert attribute_description.label.encode(response.charset) in response.content


def test_update_post(client, user, subject, attribute_description):
    client.force_login(user)
    url = '/subjects/{}/attributes/'.format(subject.uuid)
    response = client.post(url, {
        'd1': 1,
        'd2': 'de',
    })
    assert response.status_code == 302

    subject.refresh_from_db()
    assert subject.attributes['d1'] == 1
    assert subject.attributes['d2'] == 'de'
