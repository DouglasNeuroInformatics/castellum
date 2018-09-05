

def test_404_page_returned_if_study_is_not_provided(client, user):
    client.force_login(user)
    response = client.get('/recruitment/3/not-contacted/')
    assert response.status_code == 404


def test_200_page_returned_if_published_study_is_provided(client, user, published_study):
    client.force_login(user)
    url = '/recruitment/{}/not-contacted/'.format(published_study.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_page_returned_if_published_study_is_provided(client, user, unpublished_study):
    client.force_login(user)
    url = '/recruitment/{}/not-contacted/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 404
