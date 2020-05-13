import pytest
from model_bakery import baker

from castellum.contacts.models import Contact


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/guardians/'
    response = client.get(url)
    assert response.status_code == 200
    assert b'create-tab' not in response.content


def test_with_parameters_200(client, user):
    client.force_login(user)
    url = '/subjects/guardians/?search=foo+bar'
    response = client.get(url)
    assert response.status_code == 200
    assert b'create-tab' in response.content


def test_match(request, client, user):
    baker.make(Contact, first_name='foo', last_name='bar')

    client.force_login(user)
    response = client.get('/subjects/guardians/?search=foo+bar')

    assert response.content.count(b'<li class="table-list-item">') == 1


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_create(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/guardians/?search=foo+bar'
    response = client.post(url, {
        'first_name': 'foo',
        'last_name': 'bar',
        'date_of_birth': '1970-01-01',
        'gender': '*',
        'privacy_level': 0,
    })
    assert b'guardian-use-auto' in response.content
    qs = Contact.objects.filter(first_name='foo', last_name='bar')
    assert qs.exists()
    assert qs.get().subject.privacy_level == 0


def test_create_invalid(client, user):
    client.force_login(user)
    url = '/subjects/guardians/?search=foo+bar'
    response = client.post(url, {
        'first_name': 'foo',
        'last_name': 'bar',
        'date_of_birth': '1970-01-01',
        'gender': '*',
    })
    assert b'guardian-use-auto' not in response.content
    assert not Contact.objects.filter(first_name='foo', last_name='bar').exists()
