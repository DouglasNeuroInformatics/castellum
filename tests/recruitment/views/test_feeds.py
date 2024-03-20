import datetime

import pytest
from model_bakery import baker

from castellum.recruitment.models import Participation


def test_feed_for_study(client, member, study):
    baker.make(
        Participation,
        study=study,
        status=Participation.FOLLOWUP_APPOINTED,
        _fill_optional=['followup_time', 'followup_date'],
    )

    url = f'/recruitment/{study.pk}/followups/?token={member.token}'
    response = client.get(url)
    assert response.status_code == 200


def test_feed_for_draft_study(client, member, draft_study):
    url = f'/recruitment/{draft_study.pk}/followups/?token={member.token}'
    response = client.get(url)
    assert response.status_code == 404


def test_feed_for_study_without_token(client, draft_study):
    response = client.get(f'/recruitment/{draft_study.pk}/followups/')
    assert response.status_code == 403


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_feed_for_user(request, client, user_fixture, participation):
    user = request.getfixturevalue(user_fixture)

    participation.followup_date = datetime.date.today()
    participation.save()

    response = client.get(f'/recruitment/followups/?token={user.token}')
    assert response.status_code == 200
    assert response.content.count(b'BEGIN:VEVENT') == 1


def test_feed_for_user_without_token(client, user, participation):
    response = client.get('/recruitment/followups/')
    assert response.status_code == 403
