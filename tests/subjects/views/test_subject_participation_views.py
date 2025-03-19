import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    'data_protection_officer',
])
def test_list_200(request, client, user_fixture, invited):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get(f'/subjects/{invited.subject.pk}/participations/')
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


def test_recruit_200(client, user, subject):
    client.force_login(user)
    response = client.get(f'/subjects/{subject.pk}/participations/recruit/')
    assert response.status_code == 200
    assert b'No matching studies found' in response.content


def test_recruit_200_with_study(client, member, subject, study):
    client.force_login(member)
    response = client.get(f'/subjects/{subject.pk}/participations/recruit/')
    assert response.status_code == 200
    assert b'No matching studies found' not in response.content


def test_add_200(client, user, subject):
    client.force_login(user)
    response = client.get(f'/subjects/{subject.pk}/participations/add/?q=test')
    assert response.status_code == 200
    assert b'No matching studies found' in response.content
