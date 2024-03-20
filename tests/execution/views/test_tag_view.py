from model_bakery import baker

from castellum.recruitment.models import ExecutionTag


def test_create(client, member, study):
    client.force_login(member)
    url = f'/execution/{study.pk}/tags/'
    response = client.post(url, {
        'action': 'create',
        'name': 'test_tag',
        'color': 'info',
    })
    assert response.status_code == 302
    assert ExecutionTag.objects.filter(name='test_tag').exists()


def test_save(client, member, study):
    client.force_login(member)
    url = f'/execution/{study.pk}/tags/'
    tag = baker.make(ExecutionTag, study=study, name='old')
    response = client.post(url, {
        'action': 'save',
        f'{tag.id}-name': 'new',
        f'{tag.id}-color': 'info',
        'id': tag.id,
    })
    tag.refresh_from_db()
    assert response.status_code == 302
    assert tag.name == 'new'


def test_delete(client, member, study):
    client.force_login(member)
    url = f'/execution/{study.pk}/tags/'
    tag = baker.make(ExecutionTag, study=study)
    response = client.post(url, {
        'action': 'delete',
        'id': tag.id,
    })
    assert response.status_code == 302
    assert not ExecutionTag.objects.exists()


def test_invalid(client, member, study):
    client.force_login(member)
    url = f'/execution/{study.pk}/tags/'

    response = client.post(url, {'action': 'save'})
    assert response.status_code == 200

    response = client.post(url, {'action': 'invalid'})
    assert response.status_code == 200
