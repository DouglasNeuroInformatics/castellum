import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.models import Participation


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/subjects/')
    assert response.status_code == 200
    assert b'create-tab' not in response.content


def test_with_parameters_200(client, user):
    client.force_login(user)
    response = client.post('/subjects/', {'search': 'foo bar'})
    assert response.status_code == 200
    assert b'create-tab' in response.content


@pytest.mark.parametrize('user_fixture', [
    'subject_manager',
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('receptionist', marks=pytest.mark.xfail(strict=True)),
    pytest.param('conductor', marks=pytest.mark.xfail(strict=True)),
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_match(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)

    baker.make(Contact, first_name='foo', last_name='bar')

    client.force_login(user)
    response = client.post('/subjects/', {'search': 'foo bar'})

    assert response.content.count(b'<div class="table-list-item">') == 1


@pytest.mark.parametrize('user_fixture', [
    'member',
    'receptionist',
    pytest.param('user', marks=pytest.mark.xfail(strict=True)),
])
def test_only_members(request, client, user_fixture, study_in_execution_status):
    user = request.getfixturevalue(user_fixture)

    contact = baker.make(Contact, first_name='foo', last_name='bar')
    baker.make(
        Participation,
        study=study_in_execution_status,
        subject=contact.subject,
        status=Participation.PARTICIPATING,
    )

    client.force_login(user)
    response = client.post('/subjects/', {'search': 'foo bar'})

    assert response.content.count(b'<li class="table-list-item">') == 1


def test_matches(client, member, study_in_execution_status, study):
    contact1 = baker.make(Contact, first_name='asd', last_name='asd')
    contact2 = baker.make(Contact, first_name='foo', last_name='bar')
    contact3 = baker.make(Contact, first_name='foo', last_name='bar')
    contact4 = baker.make(Contact, first_name='foo', last_name='bar')

    # no item because of name
    baker.make(
        Participation,
        study=study_in_execution_status,
        subject=contact1.subject,
        status=Participation.PARTICIPATING,
    )
    # no subitem because of study status
    baker.make(
        Participation,
        study=study,
        subject=contact2.subject,
        status=Participation.PARTICIPATING,
    )
    # no execution button because of particiaption status
    baker.make(
        Participation,
        study=study_in_execution_status,
        subject=contact3.subject,
        status=Participation.EXCLUDED,
    )
    baker.make(
        Participation,
        study=study_in_execution_status,
        subject=contact4.subject,
        status=Participation.PARTICIPATING,
    )

    client.force_login(member)
    response = client.post('/subjects/', {'search': 'foo bar'})

    assert response.content.count(b'<div class="table-list-item">') == 3
    assert response.content.count(b'<li class="table-list-item">') == 2
    assert response.content.count(b'>Recruitment</a>') == 2
    assert response.content.count(b'>Execution</a>') == 1


def test_no_create_tab_on_incomplete_name(client, user):
    client.force_login(user)
    response = client.post('/subjects/', {'search': 'foo foo@example.com'})
    assert response.status_code == 200
    assert b'create-tab' not in response.content


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_create(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.post('/subjects/', {
        'search': 'foo bar foo@example.com',
        'privacy_level': 0,
    })
    assert response.status_code == 302
    qs = Contact.objects.filter(first_name='foo', last_name='bar', email='foo@example.com')
    assert qs.exists()
    assert qs.get().subject.privacy_level == 0


def test_create_only_email(client, user):
    client.force_login(user)
    response = client.post('/subjects/', {
        'search': 'foo@example.com',
        'privacy_level': 0,
    })
    assert response.status_code == 200


def test_create_no_search(client, user):
    client.force_login(user)
    response = client.post('/subjects/', {'privacy_level': 0})
    assert response.status_code == 200
