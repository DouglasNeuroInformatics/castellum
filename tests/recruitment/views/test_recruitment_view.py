def test_200(client, member, study):
    client.force_login(member)
    url = f'/recruitment/{study.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/')
    assert response.status_code == 404


def test_404_if_draft_study(client, member, draft_study):
    client.force_login(member)
    url = f'/recruitment/{draft_study.pk}/'
    response = client.get(url)
    assert response.status_code == 404
