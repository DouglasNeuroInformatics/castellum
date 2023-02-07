import pytest

FORM_DEFAULTS = {
    'name': 'name',
    'contact_person': 'contact_person',
    'phone': '09868 94060',
    'email': 'test@example.com',
    'min_subject_count': 0,
}


@pytest.mark.smoketest
def test_200(client, member, study):
    client.force_login(member)
    response = client.get('/studies/{}/update/'.format(study.pk))
    assert response.status_code == 200


def test_tags(client, member, study):
    client.force_login(member)

    for tags in [['foo', 'bar'], ['foo', 'baz'], []]:
        client.post('/studies/{}/update/'.format(study.pk), {
            'tags': tags, **FORM_DEFAULTS
        })

        study.refresh_from_db()
        assert set(study.tags) == set(tags)


def test_tags_error(client, member, study):
    client.force_login(member)

    response = client.post('/studies/{}/update/'.format(study.pk), {'tags': ['foo']})
    assert response.status_code == 200
    assert b'<option value="foo" selected>foo</option>' in response.content
