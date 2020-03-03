import pytest

from castellum.recruitment.models import ParticipationRequest


@pytest.mark.smoketest
def test_200(client, member, participation_request, attributeset):
    participation_request.status = ParticipationRequest.NOT_CONTACTED
    participation_request.save()

    participation_request.subject.attributeset = attributeset

    client.force_login(member)
    response = client.get('/recruitment/{}/{}/update-attributeset/'.format(
        participation_request.study.pk, participation_request.pk
    ))
    assert response.status_code == 200
