import pytest
from model_bakery import baker

from castellum.recruitment.models import Participation
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


def test_finish_deletes_assignments(
    client, member, recruiter, study_in_execution_status, participation
):
    client.force_login(member)

    participation.assigned_recruiter = recruiter.studymembership_set.get(
        study=study_in_execution_status
    )
    participation.status = Participation.INVITED
    participation.save()

    client.post('/studies/{}/finish/'.format(study_in_execution_status.pk))
    participation.refresh_from_db()

    assert participation.assigned_recruiter is None
