import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.pseudonyms.models import Domain
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    'data_protection_coordinator',
])
def test_detail_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_data_protection_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/data-protection/'
    response = client.get(url)
    assert response.status_code == 200


def test_data_protection_post_valid(client, user, subject):
    client.force_login(user)
    assert subject.privacy_level == 0

    url = f'/subjects/{subject.pk}/data-protection/'
    response = client.post(url, {
        'privacy_level': 1,
    })
    assert response.status_code == 302

    subject.refresh_from_db()
    assert subject.privacy_level == 1


def test_data_protection_post_invalid_privacy_level(client, user, subject):
    client.force_login(user)

    url = f'/subjects/{subject.pk}/data-protection/'
    response = client.post(url, {
        'privacy_level': 2,
    })
    assert response.status_code == 200
    assert b'Please choose lower privacy level for the subject.' in response.content


def test_data_protection_post_invalid_to_be_deleted_consent(client, user, subject):
    client.force_login(user)

    baker.make(Consent, _fill_optional=['document'], subject=subject)

    url = f'/subjects/{subject.pk}/data-protection/'
    response = client.post(url, {
        'privacy_level': 1,
        'to_be_deleted': 'on',
    })
    msg = b'Subjects can either be marked for deletion or have recruitment consent, not both.'
    assert response.status_code == 200
    assert msg in response.content


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_consent_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/data-protection/consent/'
    response = client.get(url)
    assert response.status_code == 200


def test_consent_post(request, client, user, subject):
    client.force_login(user)

    document = baker.make(ConsentDocument)

    url = f'/subjects/{subject.pk}/data-protection/consent/'
    response = client.post(url, {
        'document': document.pk,
    })
    assert response.status_code == 302
    assert subject.consent.document == document


def test_consent_create_document(request, client, user, subject):
    client.force_login(user)

    assert not ConsentDocument.objects.exists()
    url = f'/subjects/{subject.pk}/data-protection/consent/'
    client.get(url)
    assert ConsentDocument.objects.exists()


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_additional_info_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/additional-info/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_contact_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/contact/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    'data_protection_coordinator',
])
def test_partcipation_list_200(request, client, user_fixture, participation):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{participation.subject.pk}/participations/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_delete_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/delete/'
    response = client.get(url)
    assert response.status_code == 200


def test_delete_post(client, user, contact):
    client.force_login(user)
    url = f'/subjects/{contact.subject.pk}/delete/'
    client.post(url)
    assert not Contact.objects.filter(pk=contact.pk).exists()


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_participation_delete_post(request, client, user_fixture, participation):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/participations/{}/delete/'.format(
        participation.subject.pk, participation.pk
    )
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_pseudonyms_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    baker.make(Domain)
    url = f'/subjects/{subject.pk}/pseudonyms/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_pseudonym_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    domain = baker.make(Domain)
    url = f'/subjects/{subject.pk}/pseudonyms/{domain.key}/'
    response = client.get(url)
    assert response.status_code == 200
