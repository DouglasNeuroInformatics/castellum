

def test_404_page_returned_if_study_is_not_provided(client, user):
    client.force_login(user)
    response = client.get('/recruitment/3/')
    assert response.status_code == 404


def test_200_page_returned_if_study_is_provided(client, user, study):
    client.force_login(user)
    url = '/recruitment/{}/'.format(study.pk)
    response = client.get(url)
    assert response.status_code == 200
