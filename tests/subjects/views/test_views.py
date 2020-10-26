import datetime

import pytest

from castellum.contacts.models import Contact


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    'data_protection_coordinator',
])
def test_detail_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.subject.slug)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_data_protection_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/data-protection/'.format(contact.subject.slug)
    response = client.get(url)
    assert response.status_code == 200


def test_data_protection_post_valid(client, user, contact):
    client.force_login(user)
    assert contact.subject.privacy_level == 0

    url = '/subjects/{}/data-protection/'.format(contact.subject.slug)
    response = client.post(url, {
        'privacy_level': 1,
    })
    assert response.status_code == 302

    del contact.subject  # invalidate cache
    assert contact.subject.privacy_level == 1


def test_data_protection_post_invalid_privacy_level(client, user, contact):
    client.force_login(user)

    url = '/subjects/{}/data-protection/'.format(contact.subject.slug)
    response = client.post(url, {
        'privacy_level': 2,
    })
    assert response.status_code == 200
    assert b'Please choose lower privacy level for the subject.' in response.content


def test_data_protection_post_invalid_to_be_deleted_consent(client, user, contact):
    client.force_login(user)

    url = '/subjects/{}/data-protection/'.format(contact.subject.slug)
    response = client.post(url, {
        'privacy_level': 1,
        'to_be_deleted': 'on',
        'consent_status': 'confirmed',
    })
    msg = b'Subjects can either be marked for deletion or have recruitment consent, not both.'
    assert response.status_code == 200
    assert msg in response.content


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_additional_info_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/additional-info/'.format(contact.subject.slug)
    response = client.get(url)
    assert response.status_code == 200


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
    url = '/subjects/{}/contact/'.format(contact.subject.slug)
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
    url = '/subjects/{}/participations/'.format(participation.subject.slug)
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
    url = '/subjects/{}/export/'.format(contact.subject.slug)
    response = client.get(url)
    assert response.status_code == 200


def test_export_requested(client, user, contact):
    contact.subject.export_requested = datetime.date.today()
    contact.subject.save()

    client.force_login(user)
    url = '/subjects/{}/export/'.format(contact.subject.slug)
    response = client.get(url)

    assert response.status_code == 200
    assert b'<h1>Subject</h1>' in response.content


def test_export_post(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/export/'.format(contact.subject.slug)

    client.post(url)
    del contact.__dict__['subject']  # clear cached_property
    assert contact.subject.export_requested

    client.post(url)
    del contact.__dict__['subject']  # clear cached_property
    assert not contact.subject.export_requested


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
    url = '/subjects/{}/delete/'.format(contact.subject.slug)
    response = client.get(url)
    assert response.status_code == 200


def test_delete_post(client, user, contact):
    client.force_login(user)
    url = '/subjects/{}/delete/'.format(contact.subject.slug)
    client.post(url)
    assert not Contact.objects.filter(pk=contact.pk).exists()


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    'data_protection_coordinator',
])
def test_coverletter_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/coverletter.docx'.format(contact.subject.slug)
    response = client.get(url)
    assert response.status_code == 200
