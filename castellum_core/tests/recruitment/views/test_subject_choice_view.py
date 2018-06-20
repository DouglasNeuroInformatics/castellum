

def test_404_page_returned_if_study_is_not_provided(client, user):
    client.login(username=user.username, password=user.password)
    response = client.get('recruitment/3', follow='True')
    assert response.status_code == 404
