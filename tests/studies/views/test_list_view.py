from model_bakery import baker

from castellum.studies.models import Study


def test_list_membership_my(client, user):
    client.force_login(user)

    studies = baker.make(Study, _quantity=3)
    studies[0].members.add(user)

    response = client.get('/studies/')
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
