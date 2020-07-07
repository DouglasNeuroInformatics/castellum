import pytest

from castellum.recruitment.models import Participation


@pytest.mark.smoketest
def test_data_protection_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    response = client.get('/recruitment/{}/{}/update-data-protection/'.format(
        participation.study.pk, participation.pk
    ))
    assert response.status_code == 200


@pytest.mark.smoketest
def test_additional_info_200(client, member, participation):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    client.force_login(member)
    response = client.get('/recruitment/{}/{}/update-additional-info/'.format(
        participation.study.pk, participation.pk
    ))
    assert response.status_code == 200
