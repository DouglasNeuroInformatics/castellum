from castellum.recruitment import attribute_exporters
from castellum.recruitment.models import AttributeDescription

ATTRIBUTES = {
    'd1': 1,
    'd2': 'de',
    'd3': '1970-01-01',
}

JSON_SCHEMA = """{
    "properties": {
        "Date of birth": {
            "format": "date",
            "type": "string"
        },
        "Handedness": {
            "enum": [
                "Right",
                "Left"
            ],
            "type": "string"
        },
        "Highest degree": {
            "enum": [
                "No degree",
                "Elementary school",
                "Hauptschule",
                "Mittlere Reife",
                "Abitur",
                "Bachelor",
                "Master"
            ],
            "type": "string"
        },
        "Language": {
            "type": "string"
        },
        "id": {
            "type": "string"
        }
    },
    "type": "object"
}"""

JSON_DATA = """[
    {
        "Date of birth": "1970-01-01",
        "Handedness": "Right",
        "Language": "de",
        "id": "test"
    }
]"""

BIDS_SCHEMA = """{
    "date_of_birth": {},
    "handedness": {
        "Levels": {
            "1": "Right",
            "2": "Left"
        }
    },
    "highest_degree": {
        "Levels": {
            "3": "No degree",
            "4": "Elementary school",
            "5": "Hauptschule",
            "6": "Mittlere Reife",
            "7": "Abitur",
            "8": "Bachelor",
            "9": "Master"
        }
    },
    "language": {}
}"""

BIDS_DATA = """participant_id\thandedness\tlanguage\tdate_of_birth\thighest_degree\r
sub-test\t1\tde\t1970-01-01\tn/a\r
"""


def test_json_schema(attribute_descriptions, db):
    exporter = attribute_exporters.JSONExporter()
    descriptions = AttributeDescription.objects.all()
    assert exporter.get_schema(descriptions) == JSON_SCHEMA


def test_json_data(attribute_descriptions, contact):
    exporter = attribute_exporters.JSONExporter()
    descriptions = AttributeDescription.objects.all()
    contact.subject.attributes = ATTRIBUTES
    subjects = [('test', contact.subject)]
    assert exporter.get_data(descriptions, subjects) == JSON_DATA


def test_bids_schema(attribute_descriptions, db):
    exporter = attribute_exporters.BIDSExporter()
    descriptions = AttributeDescription.objects.all()
    assert exporter.get_schema(descriptions) == BIDS_SCHEMA


def test_bids_data(attribute_descriptions, contact):
    exporter = attribute_exporters.BIDSExporter()
    descriptions = AttributeDescription.objects.all()
    contact.subject.attributes = ATTRIBUTES
    subjects = [('test', contact.subject)]
    assert exporter.get_data(descriptions, subjects) == BIDS_DATA
