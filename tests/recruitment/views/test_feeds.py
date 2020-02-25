import datetime

import pytest


def test_feed_for_started_study(client, member, started_study):
    response = client.get('/recruitment/{}/followups/?token={}'.format(
        started_study.pk, member.token
    ))
    assert response.status_code == 200


def test_feed_for_not_started_study(client, member, study):
    response = client.get('/recruitment/{}/followups/?token={}'.format(
        study.pk, member.token
    ))
    assert response.status_code == 404


def test_feed_for_study_without_token(client, study):
    response = client.get('/recruitment/{}/followups/'.format(study.pk))
    assert response.status_code == 403


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_feed_for_user(request, client, user_fixture, participation_request):
    user = request.getfixturevalue(user_fixture)

    participation_request.followup_date = datetime.date.today()
    participation_request.save()

    response = client.get('/recruitment/followups/{}/?token={}'.format(user.pk, user.token))
    assert response.status_code == 200
    assert response.content.count(b'BEGIN:VEVENT') == 1


def test_feed_for_user_without_token(client, user, participation_request):
    response = client.get('/recruitment/followups/{}/'.format(user.pk))
    assert response.status_code == 403
