import pytest

from castellum.participations.models import Participation


@pytest.mark.smoketest
def test_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    response = client.get('/recruitment/{}/{}/update-contact/'.format(
        participation.study.pk, participation.pk
    ))
    assert response.status_code == 200
