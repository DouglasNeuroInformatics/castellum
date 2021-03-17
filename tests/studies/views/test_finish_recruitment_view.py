import pytest
from model_bakery import baker

from castellum.studies.models import Study
from castellum.studies.models import StudyMembership


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_finish(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    baker.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.status = Study.EDIT
    study.save()

    response = client.post('/studies/{}/finish/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.status is Study.FINISHED


@pytest.mark.parametrize('initial_status', [
    Study.EDIT,
    Study.EXECUTION,
])
def test_resume(client, member, study, initial_status):
    client.force_login(member)

    study.status = initial_status
    study.save()

    client.post('/studies/{}/finish/'.format(study.pk))

    study.refresh_from_db()
    assert study.status is Study.FINISHED

    client.post('/studies/{}/finish/'.format(study.pk))

    study.refresh_from_db()
    assert study.status is initial_status
