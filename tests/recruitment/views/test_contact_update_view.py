from castellum.recruitment.models import ParticipationRequest


def test_200(client, member, participation_request):
    participation_request.status = ParticipationRequest.NOT_CONTACTED
    participation_request.save()

    client.force_login(member)
    response = client.get('/recruitment/{}/{}/update-contact/'.format(
        participation_request.study.pk, participation_request.pk))
    assert response.status_code == 200
