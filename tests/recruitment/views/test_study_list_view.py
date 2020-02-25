def test_list_count_own_tab(client, member, started_study):
    client.force_login(member)
    response = client.get('/recruitment/')

    assert response.status_code == 200
