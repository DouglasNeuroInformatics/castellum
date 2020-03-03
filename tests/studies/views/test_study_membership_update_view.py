import pytest

from castellum.studies.models import StudyMembership


@pytest.mark.smoketest
def test_200(client, member, study):
    client.force_login(member)
    membership = StudyMembership.objects.get(study=study, user=member)
    response = client.get('/studies/{}/members/{}/'.format(study.pk, membership.pk))
    assert response.status_code == 200
