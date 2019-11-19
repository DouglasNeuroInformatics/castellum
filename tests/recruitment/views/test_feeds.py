from django.utils import timezone

import pytest


def test_feed_for_study_in_execution_status(client, study_in_execution_status):
    response = client.get('/recruitment/{}/followups/'.format(study_in_execution_status.pk))
    assert response.status_code == 200


def test_feed_for_study_in_edit_status(client, study_in_edit_status):
    response = client.get('/recruitment/{}/followups/'.format(
        study_in_edit_status.pk))
    assert response.status_code == 404


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_officer', marks=pytest.mark.xfail(strict=True)),
])
def test_feed_for_user(request, client, user_fixture, participation_request):
    user = request.getfixturevalue(user_fixture)

    participation_request.followup = timezone.now()
    participation_request.save()

    response = client.get('/recruitment/followups/{}/'.format(user.pk))
    assert response.status_code == 200
    assert response.content.count(b'BEGIN:VEVENT') == 1
