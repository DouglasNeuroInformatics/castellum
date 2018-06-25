

def test_404_page_returned_if_study_is_not_provided(client, user, subject):
    client.force_login(user)
    url = '/recruitment/3/{}/'.format(subject.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_200_page_returned_if_study_is_provided(client, user, study, subject):
    client.force_login(user)
    url = '/recruitment/{}/{}/'.format(study.pk, subject.pk)
    response = client.get(url)
    assert response.status_code == 200
