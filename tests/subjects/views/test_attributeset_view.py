import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_update_200(request, client, user_fixture, attributeset, attribute_description):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/{}/attributes/'.format(attributeset.subject.pk, attributeset.subject.slug)
    response = client.get(url)
    assert response.status_code == 200
    assert attribute_description.label.encode(response.charset) in response.content


def test_update_post(client, user, attributeset, attribute_description):
    client.force_login(user)
    url = '/subjects/{}/{}/attributes/'.format(attributeset.subject.pk, attributeset.subject.slug)
    response = client.post(url, {
        'd1': 1,
        'd2': 'de',
        'd3': '2018-01-01',
    })
    assert response.status_code == 302

    attributeset.refresh_from_db()
    assert attributeset.data['d1'] == 1
    assert attributeset.data['d2'] == 'de'
    assert attributeset.data['d3'] == '2018-01-01'


def test_update_blocked(client, user, attributeset, attribute_description):
    attribute_description.privacy_level_write = 2
    attribute_description.save()

    client.force_login(user)
    url = '/subjects/{}/{}/attributes/'.format(attributeset.subject.pk, attributeset.subject.slug)
    response = client.get(url)

    assert response.status_code == 200
    assert attribute_description.label.encode(response.charset) not in response.content


def test_update_blocked_post(client, user, attributeset, attribute_description):
    attribute_description.privacy_level_write = 2
    attribute_description.save()
    attributeset.data[attribute_description.json_key] = 'old'
    attributeset.save()

    client.force_login(user)
    url = '/subjects/{}/{}/attributes/'.format(attributeset.subject.pk, attributeset.subject.slug)
    response = client.post(url, {
        'd1': 1,
        'd2': 'de',
        'd3': '2018-01-01',
    })
    assert response.status_code == 302

    attributeset.refresh_from_db()
    assert attributeset.data[attribute_description.json_key] == 'old'
