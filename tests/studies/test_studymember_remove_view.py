import pytest
from model_mommy import mommy

from castellum.studies.models import StudyMembership


@pytest.mark.django_db
def test_user_cannot_remove_themselves_from_study(client, user, study):

    membership = mommy.make(StudyMembership, user=user, study=study)

    client.force_login(user)

    response = client.post('/studies/{}/members/{}/delete/'.format(study.pk, membership.pk))

    assert response.status_code == 400

    assert StudyMembership.objects.last().user.username == user.username
