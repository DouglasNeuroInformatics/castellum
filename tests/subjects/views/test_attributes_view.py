import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_update_200(request, client, user_fixture, contact, attribute_description):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/attributes/'.format(contact.subject.slug)
    response = client.get(url)
    assert response.status_code == 200
    assert attribute_description.label.encode(response.charset) in response.content


def test_update_post(client, user, contact, attribute_description):
    client.force_login(user)
    url = '/subjects/{}/attributes/'.format(contact.subject.slug)
    response = client.post(url, {
        'd1': 1,
        'd2': 'de',
        'd3': '2018-01-01',
    })
    assert response.status_code == 302

    contact.subject.refresh_from_db()
    assert contact.subject.attributes['d1'] == 1
    assert contact.subject.attributes['d2'] == 'de'
    assert contact.subject.attributes['d3'] == '2018-01-01'


def test_update_blocked(client, user, contact, attribute_description):
    attribute_description.privacy_level_write = 2
    attribute_description.save()

    client.force_login(user)
    url = '/subjects/{}/attributes/'.format(contact.subject.slug)
    response = client.get(url)

    assert response.status_code == 200
    assert attribute_description.label.encode(response.charset) not in response.content


def test_update_blocked_post(client, user, contact, attribute_description):
    attribute_description.privacy_level_write = 2
    attribute_description.save()
    contact.subject.attributes[attribute_description.json_key] = 'old'
    contact.save()

    client.force_login(user)
    url = '/subjects/{}/attributes/'.format(contact.subject.slug)
    response = client.post(url, {
        'd1': 1,
        'd2': 'de',
        'd3': '2018-01-01',
    })
    assert response.status_code == 302

    contact.refresh_from_db()
    assert contact.subject.attributes[attribute_description.json_key] == 'old'
