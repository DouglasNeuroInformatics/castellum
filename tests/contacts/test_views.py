def test_detail_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_search_200(client, user):
    client.force_login(user)
    url = '/subjects/search/'
    response = client.get(url)
    assert response.status_code == 200


def test_prelude_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/create/'
    response = client.get(url)
    assert response.status_code == 200


def test_create_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/create/form/'
    response = client.get(url)
    assert response.status_code == 200


def test_create_with_parameter_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/create/form/?first_name=test'
    response = client.get(url)
    assert response.status_code == 200


def test_update_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/update/'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_update_with_parameter_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/update/?first_name=test'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_requestcreate_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/request/'
    response = client.get(url)
    assert response.status_code == 200


def test_requestcreate_with_parameters_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/request/?first_name=test&last_name=test&date_of_birth=2000-02-02'
    response = client.get(url)
    assert response.status_code == 200


def test_export_200(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/export/'.format(contact.pseudonym)
    response = client.get(url)
    assert response.status_code == 200
