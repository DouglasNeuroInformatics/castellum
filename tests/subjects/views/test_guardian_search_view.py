def test_guardian_search_200(client, user):
    client.force_login(user)
    url = '/subjects/guardians/?first_name=Test&last_name=Test'
    response = client.get(url)
    assert 200 == response.status_code
