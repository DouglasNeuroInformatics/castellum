import json

def test_admin_import_attributedescriptions(client, user, tmpdir):

    user.is_staff = True
    user.save()

    client.force_login(user)
    url = '/admin/recruitment/attributedescription/import/'

    json_file = tmpdir.join("attrs.json")

    data = {
                "descriptions": [
                    {
                        "field_type": "AgeField",
                        "_filter_label": "Age",
                        "help_text": "",
                        "label": "Date of birth",
                        "weight": 0,
                        "choices": [],
                        "privacy_level": 0
                    }
                ]
            }

    json_file.write(json.dumps(data))

    response = client.post(url, {'file': json_file})
    assert response.status_code == 200
