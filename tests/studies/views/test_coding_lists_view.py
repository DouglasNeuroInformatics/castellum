import pytest
from model_bakery import baker

from castellum.pseudonyms.models import CodingList


@pytest.mark.smoketest
def test_200(client, study, member):
    client.force_login(member)
    response = client.get('/studies/{}/coding-lists/'.format(study.pk))
    assert response.status_code == 200


def test_add(client, study, member):
    client.force_login(member)
    response = client.post('/studies/{}/coding-lists/'.format(study.pk), {
        'action': 'add',
    })
    assert response.status_code == 302
    assert study.coding_lists.count() == 1


def test_name(client, study, member):
    client.force_login(member)
    coding_list = baker.make(CodingList, context=study)
    response = client.post('/studies/{}/coding-lists/'.format(study.pk), {
        'action': 'name',
        'coding_list': coding_list.key,
        'name': 'foo',
    })
    assert response.status_code == 302
    coding_list.refresh_from_db()
    assert coding_list.name == 'foo'


def test_delete(client, study, member):
    client.force_login(member)
    coding_list = study.coding_lists.create()
    response = client.post('/studies/{}/coding-lists/{}/'.format(study.pk, coding_list.key))
    assert response.status_code == 302
    assert study.coding_lists.count() == 0
