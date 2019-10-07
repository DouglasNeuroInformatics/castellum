from django.utils import timezone

import pytest


def test_feed_for_study_in_execution_mode(client, study_in_execution_mode):
    url = '/recruitment/{}/appointments/'.format(study_in_execution_mode.default_group.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_feed_for_study_in_edit_mode(client, study_in_edit_mode):
    response = client.get('/recruitment/{}/appointments/'.format(
        study_in_edit_mode.default_group.pk))
    assert response.status_code == 404


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_feed_for_user(request, client, user_fixture, participation_request):
    user = request.getfixturevalue(user_fixture)

    participation_request.appointment = timezone.now()
    participation_request.save()

    response = client.get('/recruitment/appointments/{}/'.format(user.pk))
    assert response.status_code == 200
    assert response.content.count(b'BEGIN:VEVENT') == 1
