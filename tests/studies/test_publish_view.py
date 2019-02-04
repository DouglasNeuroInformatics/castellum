import pytest
from model_mommy import mommy

from castellum.studies.models import StudyMembership


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_publish(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    mommy.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.published = False
    study.save()

    response = client.post('/studies/{}/publish/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.published is True


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_unpublish(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    mommy.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.published = True
    study.save()

    response = client.post('/studies/{}/publish/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.published is False
