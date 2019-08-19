import pytest
from castellum.studies.models import Study
from castellum.studies.models import StudyMembership
from model_mommy import mommy


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_start_recruitment(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    mommy.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.study_mode = Study.EDIT
    study.save()

    response = client.post('/studies/{}/start-recruitment/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.study_mode is Study.EXECUTION


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
])
def test_stop_recruitment(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    mommy.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.study_mode = Study.EXECUTION
    study.save()

    response = client.post('/studies/{}/start-recruitment/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.study_mode is Study.EDIT
