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


def test_update_other_study(client, user, subject_filter_group, study):
    client.force_login(user)
    url = '/recruitment/filter/{}/{}/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_delete_200(client, user, subject_filter_group):
    client.force_login(user)
    study = subject_filter_group.study
    url = '/recruitment/filter/{}/{}/delete/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_delete_other_study(client, user, subject_filter_group, study):
    client.force_login(user)
    url = '/recruitment/filter/{}/{}/delete/'.format(study.pk, subject_filter_group.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_nonempty_list_200(client, user, subject_filter_group, unpublished_study):
    client.force_login(user)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_empty_list_302(client, user, unpublished_study):
    client.force_login(user)
    url = '/recruitment/filter/{}/'.format(unpublished_study.pk)
    response = client.get(url)
    assert response.status_code == 302
