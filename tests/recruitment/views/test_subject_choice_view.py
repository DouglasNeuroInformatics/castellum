

def test_404_page_returned_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/')
    assert response.status_code == 404


def test_200_page_returned_if_published_study_is_provided(client, member, published_study):
    client.force_login(member)
    url = '/recruitment/{}/'.format(published_study.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_page_returned_if_published_study_is_provided(client, member, unpublished_study):
    client.force_login(member)
    url = '/recruitment/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 404
