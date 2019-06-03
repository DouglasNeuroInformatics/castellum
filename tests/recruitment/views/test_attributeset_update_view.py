from castellum.recruitment.models import ParticipationRequest


def test_200(client, member, participation_request, attributeset):
    participation_request.study.published = True
    participation_request.study.save()
    participation_request.status = ParticipationRequest.NOT_CONTACTED
    participation_request.save()

    participation_request.subject.attributeset = attributeset

    client.force_login(member)
    response = client.get('/recruitment/{}/{}/update-attributeset/'.format(
        participation_request.study.pk, participation_request.pk))
    assert response.status_code == 200
