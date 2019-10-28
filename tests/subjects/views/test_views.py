import pytest


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_officer',
])
def test_search_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/subjects/')
    assert 200 == response.status_code


def test_search_with_parameters_200(client, user):
    client.force_login(user)
    url = '/subjects/?first_name=Test&last_name=Test'
    response = client.get(url)
    assert 200 == response.status_code


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_officer', marks=pytest.mark.xfail(strict=True)),
])
def test_create_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/'
    response = client.post(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_officer',
])
def test_detail_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_detail_with_attributeset_200(client, user, contact, attributeset):
    client.force_login(user)
    url = '/subjects/{}/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_officer', marks=pytest.mark.xfail(strict=True)),
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


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_officer', marks=pytest.mark.xfail(strict=True)),
])
def test_contact_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/contact/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_officer',
])
def test_export_200(request, client, user_fixture, contact):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/{}/export/'.format(contact.subject.pk)
    response = client.get(url)
    assert response.status_code == 200
