def test_detail_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200
