import pytest
from model_bakery import baker

from castellum.studies.models import StudyMembership


@pytest.mark.smoketest
def test_remove_member_200(client, admin, study):
    client.force_login(admin)
    membership = baker.make(StudyMembership, study=study)
    response = client.get(f'/studies/{study.pk}/members/{membership.pk}/delete/')
    assert response.status_code == 200


def test_remove_member(client, admin, study):
    client.force_login(admin)
    membership = baker.make(StudyMembership, study=study)
    response = client.post(f'/studies/{study.pk}/members/{membership.pk}/delete/')
    assert response.status_code == 302
    assert not StudyMembership.objects.filter(pk=membership.pk).exists()


def test_users_cannot_remove_themselves_from_study(client, admin, study):
    client.force_login(admin)
    membership = baker.make(StudyMembership, study=study, user=admin)
    response = client.post(f'/studies/{study.pk}/members/{membership.pk}/delete/')
    assert response.status_code == 400
    assert StudyMembership.objects.filter(pk=membership.pk).exists()
