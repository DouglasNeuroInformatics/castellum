def test_detail_200(client, user, attributeset):
    client.force_login(user)
    url = '/recruitment/attributes/{}/'.format(attributeset.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_update_200(client, user, attributeset, attribute_description):
    client.force_login(user)
    url = '/recruitment/attributes/{}/update/'.format(attributeset.pseudonym)
    response = client.get(url)
    assert response.status_code == 200
    assert attribute_description.label.encode(response.charset) in response.content


def test_update_post(client, user, attributeset, attribute_description):
    client.force_login(user)
    url = '/recruitment/attributes/{}/update/'.format(attributeset.pseudonym)
    response = client.post(url, {
        'handedness': 1,
        'first_language': 'de',
        'date_of_birth': '2018-01-01',
    })
    assert response.status_code == 302

    attributeset.refresh_from_db()
    assert attributeset.data['handedness'] == 1
    assert attributeset.data['first_language'] == 'de'
    assert attributeset.data['date_of_birth'] == '2018-01-01'


def test_update_blocked(client, user, attributeset, attribute_description):
    attribute_description.privacy_level = 2
    attribute_description.save()

    client.force_login(user)
    url = '/recruitment/attributes/{}/update/'.format(attributeset.pseudonym)
    response = client.get(url)

    assert response.status_code == 200
    assert attribute_description.label.encode(response.charset) not in response.content


def test_update_blocked_post(client, user, attributeset, attribute_description):
    attribute_description.privacy_level = 2
    attribute_description.save()
    attributeset.data[attribute_description.name] = 'old'
    attributeset.save()

    client.force_login(user)
    url = '/recruitment/attributes/{}/update/'.format(attributeset.pseudonym)
    response = client.post(url, {
        'handedness': 1,
        'first_language': 'de',
        'date_of_birth': '2018-01-01',
    })
    assert response.status_code == 302

    attributeset.refresh_from_db()
    assert attributeset.data[attribute_description.name] == 'old'
