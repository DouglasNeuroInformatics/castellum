

def test_404_page_returned_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/')
    assert response.status_code == 404


def test_200_page_returned_if_study_in_recruitment_mode(client,
                                                        member,
                                                        study_in_recruitment_mode):
    client.force_login(member)
    url = '/recruitment/{}/'.format(study_in_recruitment_mode.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_page_returned_if_study_in_not_recruitment_mode(client,
                                                            member,
                                                            study_not_in_recruitment_mode):
    client.force_login(member)
    url = '/recruitment/{}/'.format(study_not_in_recruitment_mode.pk)
    response = client.get(url)
    assert response.status_code == 404
