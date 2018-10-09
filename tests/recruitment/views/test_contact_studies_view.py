def test_200_without_attributeset(client, user, contact):
    client.force_login(user)
    response = client.get('/recruitment/contacts/{}/studies/'.format(contact.pseudonym))
    assert response.status_code == 200
    assert b'No attributes provided' in response.content


def test_200_with_attributeset(client, user, contact, attributeset):
    client.force_login(user)
    response = client.get('/recruitment/contacts/{}/studies/'.format(contact.pseudonym))
    assert response.status_code == 200
    assert b'No matching studies found' in response.content


def test_200_with_attributeset_and_study(client, user, contact, attributeset, published_study):
    client.force_login(user)
    response = client.get('/recruitment/contacts/{}/studies/'.format(contact.pseudonym))
    assert response.status_code == 200
    assert b'No attributes provided' not in response.content
    assert b'No matching studies found' not in response.content
