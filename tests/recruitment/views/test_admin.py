import json
from io import BytesIO

import pytest
from parler.utils.context import switch_language

from castellum.recruitment.models import AttributeDescription

URL = '/admin/recruitment/attributedescription/import/'

DATA = {
    "descriptions": [
        {
            "field_type": "AgeField",
            "_filter_label": {"en": "Age", "de": "Älter"},  # non-ascii char
            "help_text": {"en": "", "de": ""},
            "label": {"en": "Date of birth", "de": "Geburtsdatum"},
            "order": 1000,
            "choices": [],
        }
    ]
}


def test_admin_import_attributedescriptions(client, admin):
    json_file = BytesIO(json.dumps(DATA, ensure_ascii=False).encode('utf-8'))

    client.force_login(admin)
    response = client.post(URL, {'file': json_file})

    assert response.status_code == 200
    assert b'UTF-8' not in response.content
    assert AttributeDescription.objects.filter(order=1000).exists()

    attr_description = AttributeDescription.objects.get(order=1000)
    with switch_language(attr_description, 'en'):
        assert attr_description.label == 'Date of birth'
        assert attr_description.filter_label == 'Age'
    with switch_language(attr_description, 'de'):
        assert attr_description.label == 'Geburtsdatum'
        assert attr_description.filter_label == 'Älter'


@pytest.mark.parametrize('encoding', ['utf-16', 'latin-1'])
def test_admin_import_attributedescriptions_bad_encoding(client, admin, encoding):
    json_file = BytesIO(json.dumps(DATA, ensure_ascii=False).encode(encoding))

    client.force_login(admin)
    response = client.post(URL, {'file': json_file})

    assert response.status_code == 200
    assert b'UTF-8' in response.content
    assert not AttributeDescription.objects.filter(order=1000).exists()
