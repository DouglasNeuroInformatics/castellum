import pytest


def test_api_study_list_view(
    client, user, study_in_execution_status, study_in_edit_status
):
    url = '/studies/api/studies/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {user.token}')

    assert response.status_code == 200
    data = response.json()
    assert len(data['studies']) == 2


def test_api_study_list_view_filter_status(
    client, user, study_in_execution_status, study_in_edit_status
):
    url = '/studies/api/studies/?status=edit'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {user.token}')
    assert response.json() == {'studies': [study_in_edit_status.pk]}

    url = '/studies/api/studies/?status=execution'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {user.token}')
    assert response.json() == {'studies': [study_in_execution_status.pk]}

    url = '/studies/api/studies/?status=finished'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {user.token}')
    assert response.json() == {'studies': []}


@pytest.mark.smoketest
def test_api_study_detail_view(client, member, study_in_execution_status):
    url = f'/studies/api/studies/{study_in_execution_status.pk}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'token {member.token}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == study_in_execution_status.name
