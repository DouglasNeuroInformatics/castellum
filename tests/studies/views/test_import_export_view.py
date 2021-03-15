from io import BytesIO


def test_import_export(client, member, study):
    client.force_login(member)

    # castellum allows longer names than the export format
    study.name = 'test'
    study.contact_person = 'test'
    study.principal_investigator = 'test'
    study.save()

    response = client.get('/studies/{}/export/'.format(study.pk))
    assert response.status_code == 200

    response = client.post('/studies/import/', {'file': BytesIO(response.content)})

    assert b'<input type="text" name="name" value="test"' in response.content
    assert b'<input type="email" name="email" maxlength="128" class="form-control is-invalid"' in response.content  # noqa
