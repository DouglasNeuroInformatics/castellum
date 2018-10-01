import pytest
from model_mommy import mommy

from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision


def test_404_page_returned_if_study_is_not_provided(client, user, participation_request):
    client.force_login(user)
    url = '/recruitment/3/{}/not-contacted/'.format(participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_404_page_returned_if_wrong_study_is_provided(client, user, participation_request,
                                                      published_study):
    client.force_login(user)
    url = '/recruitment/{}/{}/not-contacted/'.format(published_study.pk,
                                                     participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_200_page_returned_if_published_study_is_provided(client, user, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-contacted/'.format(participation_request.study.pk,
                                                     participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_404_page_returned_if_unpublished_study_is_provided(client, user, participation_request):
    participation_request.study.published = False
    participation_request.study.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-contacted/'.format(participation_request.study.pk,
                                                     participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_post_redirect(client, user, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-contacted/'.format(participation_request.study.pk,
                                                     participation_request.pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_back': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/not-contacted/'.format(participation_request.study.pk)


def test_post_redirect_from_not_reached(client, user, participation_request):
    participation_request.study.published = True
    participation_request.study.save()
    participation_request.status = ParticipationRequest.NOT_REACHED
    participation_request.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-reached/'.format(participation_request.study.pk,
                                                   participation_request.pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_back': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/not-reached/'.format(participation_request.study.pk)


def test_post_redirect_next_with_one_participation_request(client, user, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-contacted/'.format(participation_request.study.pk,
                                                     participation_request.pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_next': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/not-contacted/'.format(participation_request.study.pk)


def test_post_redirect_next_with_one_participation_request_from_not_reached(client,
                                                                            user,
                                                                            participation_request):
    participation_request.study.published = True
    participation_request.study.save()
    participation_request.status = ParticipationRequest.NOT_REACHED
    participation_request.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-reached/'.format(participation_request.study.pk,
                                                   participation_request.pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_next': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/not-reached/'.format(participation_request.study.pk)


def test_post_redirect_next_with_multiple_participation_requests(client, user, published_study):
    participation_requests = mommy.make(ParticipationRequest, study=published_study, _quantity=5)

    client.force_login(user)

    url = '/recruitment/{}/{}/not-contacted/'.format(published_study.pk,
                                                     participation_requests[3].pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/{}/not-contacted/'.format(
        published_study.pk,
        participation_requests[4].pseudonym
    )

    response = client.post(response.url, {'status': ParticipationRequest.UNSUITABLE,
                                          'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/{}/not-contacted/'.format(
        published_study.pk,
        participation_requests[2].pseudonym
    )


def test_post_redirect_next_with_multiple_participation_requests_from_not_reached(client,
                                                                                  user,
                                                                                  published_study):
    participation_requests = mommy.make(ParticipationRequest,
                                        status=ParticipationRequest.NOT_REACHED,
                                        study=published_study,
                                        _quantity=5)

    client.force_login(user)

    url = '/recruitment/{}/{}/not-reached/'.format(published_study.pk,
                                                   participation_requests[3].pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE,
                                 'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/{}/not-reached/'.format(
        published_study.pk,
        participation_requests[4].pseudonym
    )

    response = client.post(response.url, {'status': ParticipationRequest.UNSUITABLE,
                                          'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/not-reached/'.format(
        published_study.pk,
    )


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, user, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-contacted/'.format(participation_request.study.pk,
                                                     participation_request.pseudonym)
    client.post(url, {'status': ParticipationRequest.UNSUITABLE})
    participation_request = ParticipationRequest.objects.get()
    assert participation_request.updated_at.strftime('%Y-%m-%d') == '2018-01-01'


def test_create_revision_on_update(client, user, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(user)
    url = '/recruitment/{}/{}/not-contacted/'.format(participation_request.study.pk,
                                                     participation_request.pseudonym)
    client.post(url, {'status': 2})

    assert ParticipationRequestRevision.objects.count() == 2
