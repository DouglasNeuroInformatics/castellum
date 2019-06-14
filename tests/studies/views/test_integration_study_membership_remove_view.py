import pytest

from model_mommy import mommy


@pytest.mark.skip
@pytest.mark.django_db
def test_remove_any_member(client, study, study_coordinator, recruiter):
    study_membership = mommy.make("studies.StudyMembership", study=study, user=study_coordinator)
    study_membership = mommy.make("studies.StudyMembership", study=study, user=recruiter)

    client.force_login(study_coordinator)
    url = f"/studies/{study_membership.study.pk}/members/{study_membership.pk}/delete/"
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == f"/studies/{study_membership.study.pk}/members/"


@pytest.mark.skip
@pytest.mark.django_db
def test_user_cannot_remove_himself(client, study, study_coordinator):
    study_membership = mommy.make("studies.StudyMembership", study=study, user=study_coordinator)

    client.force_login(study_coordinator)
    url = f"/studies/{study_membership.study.pk}/members/{study_membership.pk}/delete/"
    response = client.post(url)

    assert response.status_code == 400
