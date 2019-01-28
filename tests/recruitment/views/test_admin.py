import json

import pytest
from parler.utils.context import switch_language

from castellum.recruitment.models import AttributeDescription

data = {
    "descriptions": [
        {
            "field_type": "AgeField",
            "weight": 1000,
            "choices": [],
            "privacy_level": 0,
            "translations": {
                "en": {
                    "_filter_label": "Age",
                    "help_text": "",
                    "label": "Date of birth",
                },
                "de": {
                    "_filter_label": "Älter",  # non-ascii char
                    "help_text": "",
                    "label": "Geburtsdatum",
                }
            },
        }
    ]
}

from io import BytesIO


@pytest.mark.parametrize('encoding', ['utf-8', 'utf-16', 'latin-1'])
def test_admin_import_attributedescriptions(client, admin, tmpdir, encoding):

    client.force_login(admin)
    url = '/admin/recruitment/attributedescription/import/'

    # json_file = tmpdir.join("attrs.json")
    # json_file.write_text(json.dumps(data), encoding)

    json_file = BytesIO()
    json_file.write(json.dumps(data).encode(encoding))
    json_file.seek(0)

    response = client.post(url, {'file': json_file})
    assert response.status_code == 200

    attr_description = AttributeDescription.objects.get(weight=1000)
    with switch_language(attr_description, 'en'):
        assert attr_description.label == 'Date of birth'
        assert attr_description.filter_label == 'Age'
    with switch_language(attr_description, 'de'):
        assert attr_description.label == 'Geburtsdatum'
        assert attr_description.filter_label == 'Älter'
