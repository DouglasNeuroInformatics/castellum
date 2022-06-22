from castellum.recruitment import attribute_exporters
from castellum.recruitment.models import AttributeDescription

ATTRIBUTES = {
    'd1': 1,
    'd2': 'de',
    'd3': '1970-01-01',
    'd5': [11, 12],
}

JSON_SCHEMA = """{
    "properties": {
        "Date of birth": {
            "format": "date",
            "privacy_level_read": 0,
            "privacy_level_write": 0,
            "type": "string"
        },
        "Handedness": {
            "enum": [
                "Right",
                "Left",
                "Ambidextrous"
            ],
            "privacy_level_read": 0,
            "privacy_level_write": 0,
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
            "privacy_level_read": 0,
            "privacy_level_write": 0,
            "type": "string"
        },
        "Instruments": {
            "items": {
                "enum": [
                    "Piano",
                    "Guitar",
                    "Drums"
                ],
                "type": "string"
            },
            "privacy_level_read": 0,
            "privacy_level_write": 0,
            "type": "array"
        },
        "Language": {
            "privacy_level_read": 0,
            "privacy_level_write": 0,
            "type": "string"
        },
        "id": {
            "type": "string"
        },
        "privacy_level": {
            "enum": [
                0,
                1,
                2
            ],
            "type": "integer"
        }
    },
    "type": "object"
}"""

JSON_DATA = """[
    {
        "Date of birth": "1970-01-01",
        "Handedness": "Right",
        "Highest degree": null,
        "Instruments": [
            "Piano",
            "Guitar"
        ],
        "Language": "de",
        "id": "test",
        "privacy_level": 0
    }
]"""

BIDS_SCHEMA = """{
    "date_of_birth": {
        "PrivacyLevelRead": 0,
        "PrivacyLevelWrite": 0,
        "TermURL": "http://purl.bioontology.org/ontology/SNOMEDCT/397669002"
    },
    "handedness": {
        "Levels": {
            "1": "Right",
            "2": "Left",
            "3": "Ambidextrous"
        },
        "PrivacyLevelRead": 0,
        "PrivacyLevelWrite": 0,
        "TermURL": "http://purl.bioontology.org/ontology/SNOMEDCT/57427004"
    },
    "highest_degree": {
        "Levels": {
            "4": "No degree",
            "5": "Elementary school",
            "6": "Hauptschule",
            "7": "Mittlere Reife",
            "8": "Abitur",
            "9": "Bachelor",
            "10": "Master"
        },
        "PrivacyLevelRead": 0,
        "PrivacyLevelWrite": 0
    },
    "instruments": {
        "Levels": {
            "11": "Piano",
            "12": "Guitar",
            "13": "Drums"
        },
        "PrivacyLevelRead": 0,
        "PrivacyLevelWrite": 0
    },
    "language": {
        "PrivacyLevelRead": 0,
        "PrivacyLevelWrite": 0
    },
    "privacy_level": {
        "Levels": {
            "0": "regular",
            "1": "increased",
            "2": "high"
        }
    }
}"""

BIDS_DATA = """participant_id\tprivacy_level\thandedness\tlanguage\tdate_of_birth\thighest_degree\tinstruments\r
sub-test\t0\t1\tde\t1970-01-01\tn/a\t11,12\r
"""


def test_json_schema(attribute_descriptions, db):
    exporter = attribute_exporters.JSONExporter()
    descriptions = AttributeDescription.objects.all()
    print(exporter.get_schema(descriptions))
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
