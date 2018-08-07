def test_detail_200(client, user, attributeset):
    client.force_login(user)
    url = '/recruitment/attributes/{}/'.format(attributeset.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_update_200(client, user, attributeset):
    client.force_login(user)
    url = '/recruitment/attributes/{}/update/'.format(attributeset.pseudonym)
    response = client.get(url)
    assert response.status_code == 200
