import pytest

from castellum.recruitment.models import Participation


@pytest.mark.smoketest
def test_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    response = client.get(
        f'/recruitment/{participation.study.pk}/{participation.pk}/update-attributes/'
    )
    assert response.status_code == 200
