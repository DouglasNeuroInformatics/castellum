def test_index_200(client, user):
    client.force_login(user)
    response = client.get('/')
    assert response.status_code == 200


def test_studies_available(client, study_coordinator):
    client.force_login(study_coordinator)
    response = client.get('/')
    assert b'Studies' in response.content


def test_studies_not_available(client, recruiter):
    client.force_login(recruiter)
    response = client.get('/')
    assert b'Studies' not in response.content
