def test_min_subjects_count_is_none(client, user, published_study):
    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = ("The minimal number of subjects is not set for this study. "
                    "Please, contact the responsible person who can set it up.")

    assert response.status_code == 200
    assert expected_msg in str(response.content)
