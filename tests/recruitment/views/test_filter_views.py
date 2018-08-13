def test_update_200(client, user, subject_filter_group):
    client.force_login(user)
    study = subject_filter_group.study
    url = '/recruitment/filter/{}/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_update_with_filter_200(client, user, subject_filter):
    client.force_login(user)
    group = subject_filter.group
    url = '/recruitment/filter/{}/{}/'.format(group.study.pk, group.pk)
    response = client.get(url)
    assert response.status_code == 200
