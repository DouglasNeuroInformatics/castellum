from datetime import datetime

import pytest


def test_feed_for_study_in_recruitment_mode(client, study_in_recruitment_mode):
    response = client.get('/recruitment/{}/appointments/'.format(study_in_recruitment_mode.pk))
    assert response.status_code == 200


def test_feed_for_study_in_edit_mode(client, study_in_edit_mode):
    response = client.get('/recruitment/{}/appointments/'.format(
        study_in_edit_mode.pk))
    assert response.status_code == 404


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_feed_for_user(request, client, user_fixture, participation_request):
    user = request.getfixturevalue(user_fixture)

    participation_request.appointment = datetime.now()
    participation_request.save()

    response = client.get('/recruitment/appointments/{}/'.format(user.pk))
    assert response.status_code == 200
    assert response.content.count(b'BEGIN:VEVENT') == 1
