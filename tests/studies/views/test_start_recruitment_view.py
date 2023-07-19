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
    client.force_login(user)

    study.status = Study.EDIT
    study.save()

    response = client.post(f'/studies/{study.pk}/start/')
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
    client.force_login(user)

    study.status = Study.EXECUTION
    study.save()

    response = client.post(f'/studies/{study.pk}/start/')
    assert response.status_code == 302

    study.refresh_from_db()
    assert study.status is Study.EDIT
