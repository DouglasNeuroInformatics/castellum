import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision


def test_404_page_returned_if_study_is_not_provided(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/3/{}/open/'.format(participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_404_page_returned_if_wrong_study_is_provided(client, member, participation_request,
                                                      published_study):
    client.force_login(member)
    url = '/recruitment/{}/{}/open/'.format(published_study.pk,
                                            participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_200_page_returned_if_published_study_is_provided(client, member, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/open/'.format(participation_request.study.pk,
                                            participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 200


def test_404_page_returned_if_unpublished_study_is_provided(client, member, participation_request):
    participation_request.study.published = False
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/open/'.format(participation_request.study.pk,
                                            participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 404


def test_post_redirect(client, member, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/open/'.format(participation_request.study.pk,
                                            participation_request.pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_back': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(participation_request.study.pk)


def test_post_redirect_next_with_one_participation_request(client, member, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/open/'.format(participation_request.study.pk,
                                            participation_request.pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_next': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(participation_request.study.pk)


def test_post_redirect_next_with_multiple_participation_requests(client,
                                                                 member,
                                                                 published_study):
    participation_requests = []
    for i in range(5):
        contact = mommy.make(Contact, pseudonym=None, privacy_level=0)
        pseudonym = resolve_pseudonym(Contact.domain, contact.pseudonym, published_study.domain)
        participation_requests.append(mommy.make(
            ParticipationRequest,
            study=published_study,
            pseudonym=pseudonym,
        ))

    client.force_login(member)

    url = '/recruitment/{}/{}/open/'.format(published_study.pk,
                                            participation_requests[3].pseudonym)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE,
                                 'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/{}/open/'.format(
        published_study.pk,
        participation_requests[4].pseudonym
    )

    response = client.post(response.url, {'status': ParticipationRequest.UNSUITABLE,
                                          'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(
        published_study.pk,
    )


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, member, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/open/'.format(participation_request.study.pk,
                                            participation_request.pseudonym)
    client.post(url, {'status': ParticipationRequest.UNSUITABLE})
    participation_request = ParticipationRequest.objects.get()
    assert participation_request.updated_at.strftime('%Y-%m-%d') == '2018-01-01'


def test_create_revision_on_update(client, member, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/open/'.format(participation_request.study.pk,
                                            participation_request.pseudonym)
    client.post(url, {'status': 2})

    assert ParticipationRequestRevision.objects.count() == 2


def test_post_redirect_from_contacts(client, member, participation_request):
    participation_request.study.published = True
    participation_request.study.save()
    participation_request.status = 1
    participation_request.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/contacts/'.format(participation_request.study.pk,
                                                participation_request.pseudonym)
    response = client.post(url, {'status': 2})
    assert response.status_code == 302
    assert response.url.startswith('/subjects/')


def test_404_on_invalid_path(client, member, participation_request):
    participation_request.study.published = True
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/foo/'.format(participation_request.study.pk,
                                           participation_request.pseudonym)
    response = client.get(url)
    assert response.status_code == 404
