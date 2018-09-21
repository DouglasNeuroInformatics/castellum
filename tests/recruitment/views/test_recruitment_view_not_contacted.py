def test_min_subjects_count_is_none(client, user, published_study):
    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = ("The minimal number of subjects is not set for this study. "
                    "Please, contact the responsible person who can set it up.")

    assert response.status_code == 200
    assert expected_msg in str(response.content)


def test_min_subjects_count_is_zero(client, user, published_study):
    published_study.min_subjects_count = 0
    published_study.save()

    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = ("This study does not require participants. "
                    "Please, contact the responsible person who can set it up.")

    assert response.status_code == 200
    assert expected_msg in str(response.content)
