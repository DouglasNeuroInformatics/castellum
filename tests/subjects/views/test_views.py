import pytest

from castellum.contacts.models import Contact


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_create_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/'
    response = client.post(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_detail_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
def test_detail_with_attributeset_200(client, user, contact, attributeset):
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_subject_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/subject/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_subject_post_valid(client, user, contact):
    client.force_login(user)
    assert contact.subject.privacy_level == 0

    url = '/subjects/{}/subject/'.format(contact.subject.pk)
    response = client.post(url, {
        'privacy_level': 1,
        'form-TOTAL_FORMS': 0,
        'form-INITIAL_FORMS': 0,
    })
    assert response.status_code == 302

    del contact.subject  # invalidate cache
    assert contact.subject.privacy_level == 1


def test_subject_post_invalid_privacy_level(client, user, contact):
    client.force_login(user)

    url = '/subjects/{}/subject/'.format(contact.subject.pk)
    response = client.post(url, {
        'privacy_level': 2,
        'form-TOTAL_FORMS': 0,
        'form-INITIAL_FORMS': 0,
    })
    assert response.status_code == 200
    assert b'Please choose lower privacy level for the subject.' in response.content


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_contact_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/contact/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_partcipation_list_200(request, client, user_fixture, participation_request):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/studyparticipation/'.format(participation_request.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_export_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/export/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_delete_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/delete/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_delete_post(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/delete/'.format(contact.subject.pk)
    client.post(url)
    assert not Contact.objects.filter(pk=contact.pk).exists()


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_coverletter_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/coverletter.docx'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200
