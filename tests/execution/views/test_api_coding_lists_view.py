from model_bakery import baker

from castellum.pseudonyms.models import CodingList


def test_api_coding_lists_view(client, conductor, study_in_execution_status):
    baker.make(CodingList, context=study_in_execution_status)
    baker.make(CodingList, context=study_in_execution_status)

    url = '/execution/api/studies/{}/coding-lists/'.format(study_in_execution_status.pk)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['coding_lists']) == 2


def test_no_general_coding_lists(client, conductor, study_in_execution_status):
    coding_list = baker.make(CodingList)
    study_in_execution_status.general_coding_lists.add(coding_list)
    conductor.general_coding_lists.add(coding_list)

    url = '/execution/api/studies/{}/coding-lists/'.format(study_in_execution_status.pk)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['coding_lists']) == 0


def test_permission(client, recruiter, study_in_execution_status):
    url = '/execution/api/studies/{}/coding-lists/'.format(study_in_execution_status.pk)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + recruiter.token)
    assert response.status_code == 403


def test_only_token_auth(client, conductor, study_in_execution_status):
    client.force_login(conductor)
    url = '/execution/api/studies/{}/coding-lists/'.format(study_in_execution_status.pk)
    response = client.get(url)
    assert response.status_code == 403
