import pytest
from model_bakery import baker

from castellum.studies.models import StudyMembership


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_start(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    baker.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    response = client.post('/studies/{}/start/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.started


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_stop(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    baker.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.started = True
    study.save()

    response = client.post('/studies/{}/start/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert not study.started
