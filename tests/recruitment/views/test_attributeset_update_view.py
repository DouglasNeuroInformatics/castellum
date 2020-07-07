import pytest

from castellum.recruitment.models import Participation


@pytest.mark.smoketest
def test_200(client, member, participation, attributeset):
    participation.status = Participation.NOT_CONTACTED
    participation.save()

    participation.subject.attributeset = attributeset

    client.force_login(member)
    response = client.get('/recruitment/{}/{}/update-attributeset/'.format(
        participation.study.pk, participation.pk
    ))
    assert response.status_code == 200
