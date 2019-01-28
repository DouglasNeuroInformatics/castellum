import json

from parler.utils.context import switch_language

from castellum.recruitment.models import AttributeDescription

data = {
    "descriptions": [
        {
            "field_type": "AgeField",
            "_filter_label": {"en": "Age", "de": "Alter"},
            "help_text": {"en": "", "de": ""},
            "label": {"en": "Date of birth", "de": "Geburtsdatum"},
            "weight": 1000,
            "choices": [],
            "privacy_level": 0
        }
    ]
}


def test_admin_imports_attributedescriptions_with_str(client, admin, tmpdir):

    client.force_login(admin)
    url = '/admin/recruitment/attributedescription/import/'

    json_file = tmpdir.join("attrs.json")
    json_file.write(json.dumps(data))

    response = client.post(url, {'file': json_file})
    assert response.status_code == 200

    attr_description = AttributeDescription.objects.get(weight=1000)
    with switch_language(attr_description, 'en'):
        assert attr_description.label == 'Date of birth'
        assert attr_description.filter_label == 'Age'
    with switch_language(attr_description, 'de'):
        assert attr_description.label == 'Geburtsdatum'
        assert attr_description.filter_label == 'Alter'
