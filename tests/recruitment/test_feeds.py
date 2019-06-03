from datetime import datetime

import pytest


def test_feed_for_published_study(client, published_study):
    response = client.get('/recruitment/{}/appointments/'.format(published_study.pk))
    assert response.status_code == 200


def test_feed_for_unpublished_study(client, unpublished_study):
    response = client.get('/recruitment/{}/appointments/'.format(unpublished_study.pk))
    assert response.status_code == 404


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_feed_for_user(request, client, user_fixture, participation_request):
    user = request.getfixturevalue(user_fixture)

    participation_request.study.published = True
    participation_request.study.save()
    participation_request.appointment = datetime.now()
    participation_request.save()

    response = client.get('/recruitment/appointments/{}/'.format(user.pk))
    assert response.status_code == 200
    assert response.content.count(b'BEGIN:VEVENT') == 1
