def test_publish(client, member, study):
    client.force_login(member)
    study.published = False
    study.save()

    response = client.post('/studies/{}/publish/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.published is True


def test_unpublish(client, member, study):
    client.force_login(member)
    study.published = True
    study.save()

    response = client.post('/studies/{}/publish/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.published is False
