import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.studies.models import Study
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision


def test_404_page_returned_if_study_is_not_provided(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/3/{}/'.format(participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_404_page_returned_if_wrong_study_is_provided(client, member, participation_request, study):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_200_page_returned_if_study_in_recruitment_mode_is_provided(client,
                                                                    member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_page_returned_if_study_in_edit_mode_is_provided(client,
                                                             member,
                                                             participation_request):
    participation_request.study.study_mode = Study.EDIT
    participation_request.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_post_redirect(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_back': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(participation_request.study.pk)


def test_post_redirect_next_with_one_participation_request(client, member, participation_request):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation_request.study.pk, participation_request.pk)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE, 'btn_next': 'value'})
    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(participation_request.study.pk)


def test_post_redirect_next_with_multiple_participation_requests(client,
                                                                 member,
                                                                 study_in_recruitment_mode):
    participation_requests = []
    for i in range(5):
        contact = mommy.make(Contact, pseudonym=None)
        subject = get_subject(Contact.domain, contact.pseudonym)
        participation_requests.append(mommy.make(
            ParticipationRequest,
            study=study_in_recruitment_mode,
            subject=subject,
        ))

    client.force_login(member)

    url = '/recruitment/{}/{}/'.format(study_in_recruitment_mode.pk, participation_requests[3].pk)
    response = client.post(url, {'status': ParticipationRequest.UNSUITABLE,
                                 'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/{}/'.format(
        study_in_recruitment_mode.pk,
        participation_requests[4].pk
    )

    response = client.post(response.url, {'status': ParticipationRequest.UNSUITABLE,
                                          'btn_next': 'value'})

    assert response.status_code == 302
    assert response.url == '/recruitment/{}/'.format(
        study_in_recruitment_mode.pk,
    )


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
    url = '/recruitment/{}/{}/?contacts'.format(participation_request.study.pk,
                                                participation_request.pk)
    response = client.post(url, {'status': 2})
    assert response.status_code == 302
    assert response.url.startswith('/subjects/')
