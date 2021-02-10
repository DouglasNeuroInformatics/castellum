import pytest

from castellum.recruitment.models import Participation


@pytest.mark.smoketest
def test_data_protection_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    response = client.get(
        f'/recruitment/{participation.study.pk}/{participation.pk}/update-data-protection/'
    )
    assert response.status_code == 200


@pytest.mark.smoketest
def test_additional_info_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    response = client.get(
        f'/recruitment/{participation.study.pk}/{participation.pk}/update-additional-info/'
    )
    assert response.status_code == 200
