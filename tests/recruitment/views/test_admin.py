import json

data = {
    "descriptions": [
        {
            "field_type": "AgeField",
            "_filter_label": {"en": "Age", "de": "Alter"},
            "help_text": {"en": "", "de": ""},
            "label": {"en": "Date of birth", "de": "Geburtsdatum"},
            "weight": 0,
            "choices": [],
            "privacy_level": 0
        }
    ]
}


def test_admin_imports_attributedescriptions_with_str(client, admin, tmpdir):

    client.force_login(admin)
    url = '/admin/recruitment/attributedescription/import/'

    json_file = tmpdir.join("attrs.json")

    # here json.dumps(data) is str
    json_file.write(json.dumps(data))

    response = client.post(url, {'file': json_file})
    assert response.status_code == 200


def test_admin_imports_attributedescriptions_with_bytes(client, admin, tmpdir):

    client.force_login(admin)
    url = '/admin/recruitment/attributedescription/import/'

    json_file = tmpdir.join("attrs.json")

    # here json.dumps(data).encode('utf8') is bytes
    json_file.write(json.dumps(data).encode('utf8'))

    response = client.post(url, {'file': json_file})
    assert response.status_code == 200
