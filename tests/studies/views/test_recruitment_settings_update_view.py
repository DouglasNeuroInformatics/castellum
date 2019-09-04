def test_200(client, member, study):
    client.force_login(member)
    response = client.get('/studies/{}/recruitmentsettings/'.format(study.pk))
    assert response.status_code == 200
