from model_bakery import baker

from castellum.studies.models import StudyMembership


def test_remove_member_200(client, user, study):
    client.force_login(user)
    membership = baker.make(StudyMembership, study=study)
    response = client.get('/studies/{}/members/{}/delete/'.format(study.pk, membership.pk))
    assert response.status_code == 200


def test_remove_member(client, user, study):
    client.force_login(user)
    membership = baker.make(StudyMembership, study=study)
    response = client.post('/studies/{}/members/{}/delete/'.format(study.pk, membership.pk))
    assert response.status_code == 302
    assert not StudyMembership.objects.filter(pk=membership.pk).exists()


def test_users_cannot_remove_themselves_from_study(client, user, study):
    client.force_login(user)
    membership = baker.make(StudyMembership, study=study, user=user)
    response = client.post('/studies/{}/members/{}/delete/'.format(study.pk, membership.pk))
    assert response.status_code == 400
    assert StudyMembership.objects.filter(pk=membership.pk).exists()
