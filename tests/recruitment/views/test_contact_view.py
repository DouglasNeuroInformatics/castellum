import pytest

from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision


def test_200(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/3/{}/'.format(participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_wrong_study_is_provided(client, member, participation_request, study):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_study_in_edit_status(client, member, participation_request):
    participation_request.study.started = False
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_post_redirect(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(participation_request.study.pk)


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    client.post(url, {'status': ParticipationRequest.UNSUITABLE})
    participation_request = ParticipationRequest.objects.get()
    assert participation_request.updated_at.strftime('%Y-%m-%d') == '2018-01-01'


def test_create_revision_on_update(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    client.post(url, {'status': 2})

    assert ParticipationRequestRevision.objects.count() == 2


def test_post_redirect_from_contacts(client, member, participation_request):
    participation_request.status = 1
    participation_request.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/?context=subjects:studyparticipation'.format(
        participation_request.study.pk, participation_request.pk
    )
    response = client.post(url, {'status': 2})
    assert response.status_code == 302
    assert response.url.startswith('/subjects/')
