from io import BytesIO


def test_import_export(client, member, study):
    client.force_login(member)

    # castellum allows longer names than the export format
    study.name = 'test'
    study.contact_person = 'test'
    study.save()
    study.studytag_set.create(name='foo')

    response = client.get(f'/studies/{study.pk}/export/')
    assert response.status_code == 200

    response = client.post('/studies/import/', {'file': BytesIO(response.content)})

    assert b'<input type="text" name="name" value="test"' in response.content
    assert b'<input type="tel" name="phone" placeholder="e.g. 030 123456" maxlength="32" class="form-control is-invalid"' in response.content  # noqa
    assert b'<option value="foo" selected>foo</option>' in response.content
