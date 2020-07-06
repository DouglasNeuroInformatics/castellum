import datetime

import pytest


def test_feed_for_study_in_execution_status(client, member, study_in_execution_status):
    response = client.get('/recruitment/{}/followups/?token={}'.format(
        study_in_execution_status.pk, member.token
    ))
    assert response.status_code == 200


def test_feed_for_study_in_edit_status(client, member, study_in_edit_status):
    response = client.get('/recruitment/{}/followups/?token={}'.format(
        study_in_edit_status.pk, member.token
    ))
    assert response.status_code == 404


def test_feed_for_study_without_token(client, study_in_edit_status):
    response = client.get('/recruitment/{}/followups/'.format(study_in_edit_status.pk))
    assert response.status_code == 403


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_feed_for_user(request, client, user_fixture, participation):
    user = request.getfixturevalue(user_fixture)

    participation.followup_date = datetime.date.today()
    participation.save()

    response = client.get('/recruitment/followups/{}/?token={}'.format(user.pk, user.token))
    assert response.status_code == 200
    assert response.content.count(b'BEGIN:VEVENT') == 1


def test_feed_for_user_without_token(client, user, participation):
    response = client.get('/recruitment/followups/{}/'.format(user.pk))
    assert response.status_code == 403
