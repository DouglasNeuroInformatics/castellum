from freezegun import freeze_time
from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.studies.models import Study


def test_list_membership_my(client, user):
    client.force_login(user)

    studies = baker.make(Study, _quantity=3)
    studies[0].members.add(user)

    response = client.get('/studies/')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 1


def test_list_membership_other(client, user, receptionist):
    client.force_login(receptionist)

    studies = baker.make(Study, _quantity=3)
    studies[0].members.add(user)

    response = client.get(f'/studies/?member={user.username}')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 0


def test_list_membership_other_superuser(client, user, admin):
    client.force_login(admin)

    studies = baker.make(Study, _quantity=3)
    studies[0].members.add(user)

    response = client.get(f'/studies/?member={user.username}')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 1


def test_list_membership_all(client, user):
    client.force_login(user)

    studies = baker.make(Study, _quantity=3)
    studies[0].members.add(user)

    response = client.get('/studies/?member=all')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 3


def test_status(client, user):
    client.force_login(user)

    baker.make(Study, _quantity=1, status=Study.DRAFT)
    baker.make(Study, _quantity=2, status=Study.EXECUTION)
    baker.make(Study, _quantity=3, status=Study.FINISHED)

    response = client.get('/studies/?member=all')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 6

    response = client.get(f'/studies/?member=all&status={Study.DRAFT}')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 1

    response = client.get(f'/studies/?member=all&status={Study.EXECUTION}')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 2

    response = client.get(f'/studies/?member=all&status={Study.FINISHED}')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 3


@freeze_time('1971-01-01')
def test_action_required_sessions_end(client, user):
    client.force_login(user)

    baker.make(Study, status=Study.FINISHED, sessions_end=None)
    baker.make(Study, status=Study.FINISHED, sessions_end='1970-01-01')
    baker.make(Study, status=Study.EXECUTION, sessions_end='1972-01-01')

    response = client.get('/studies/?member=all&status=action-required')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 0

    baker.make(Study, status=Study.DRAFT, sessions_end=None)
    baker.make(Study, status=Study.EXECUTION, sessions_end=None)
    baker.make(Study, status=Study.EXECUTION, sessions_end='1970-01-01')

    response = client.get('/studies/?member=all&status=action-required')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 2

    response = client.get('/studies/?member=all')
    assert response.content.count(b'class="table-list-item"') == 6
    assert response.content.count(b'exclamation-triangle') == 2


@freeze_time('1971-01-01')
def test_action_required_pseudonyms_delete_date(client, user):
    client.force_login(user)

    baker.make(Study, status=Study.FINISHED, pseudonyms_delete_date=None)
    baker.make(Study, status=Study.FINISHED, pseudonyms_delete_date='1970-01-01')
    baker.make(
        Study,
        status=Study.FINISHED,
        domains=[baker.make(Domain)],
        pseudonyms_delete_date='1972-01-01',
    )

    response = client.get('/studies/?member=all&status=action-required')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 0

    baker.make(
        Study,
        status=Study.FINISHED,
        domains=[baker.make(Domain)],
        pseudonyms_delete_date=None,
    )
    baker.make(
        Study,
        status=Study.FINISHED,
        domains=[baker.make(Domain)],
        pseudonyms_delete_date='1970-01-01',
    )

    response = client.get('/studies/?member=all&status=action-required')
    assert response.status_code == 200
    assert response.content.count(b'class="table-list-item"') == 2

    response = client.get('/studies/?member=all')
    assert response.content.count(b'class="table-list-item"') == 5
    assert response.content.count(b'exclamation-triangle') == 2
