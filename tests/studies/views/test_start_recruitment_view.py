import pytest
from model_bakery import baker

from castellum.studies.models import Study
from castellum.studies.models import StudyMembership


@pytest.mark.parametrize('user_fixture', [
    'study_approver',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('conductor', marks=pytest.mark.xfail(strict=True)),
])
def test_start(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    baker.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.status = Study.EDIT
    study.save()

    response = client.post('/studies/{}/start/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.status is Study.EXECUTION


@pytest.mark.parametrize('user_fixture', [
    'study_approver',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('conductor', marks=pytest.mark.xfail(strict=True)),
])
def test_stop(request, client, user_fixture, study):
    user = request.getfixturevalue(user_fixture)
    baker.make(StudyMembership, user=user, study=study)
    client.force_login(user)

    study.status = Study.EXECUTION
    study.save()

    response = client.post('/studies/{}/start/'.format(study.pk))
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.status is Study.EDIT


def test_stop_deletes_assignments(
    client, member, recruiter, study_in_execution_status, participation
):
    client.force_login(member)

    participation.assigned_user = recruiter
    participation.save()

    client.post('/studies/{}/start/'.format(study_in_execution_status.pk))
    participation.refresh_from_db()

    assert participation.assigned_user is None
