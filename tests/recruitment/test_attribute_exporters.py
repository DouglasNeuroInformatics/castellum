from castellum.recruitment import attribute_exporters
from castellum.recruitment.models import Attribute

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
            "type": "string"
        },
        "Handedness": {
            "enum": [
                "Right",
                "Left",
                "Ambidextrous"
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
        "Instruments": {
            "items": {
                "enum": [
                    "Piano",
                    "Guitar",
                    "Drums"
                ],
                "type": "string"
            },
            "type": "array"
        },
        "Language": {
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
        "TermURL": "http://purl.bioontology.org/ontology/SNOMEDCT/397669002"
    },
    "handedness": {
        "Levels": {
            "1": "Right",
            "2": "Left",
            "3": "Ambidextrous"
        },
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
        }
    },
    "instruments": {
        "Levels": {
            "11": "Piano",
            "12": "Guitar",
            "13": "Drums"
        }
    },
    "language": {},
    "privacy_level": {
        "Levels": {
            "0": "regular",
            "1": "increased",
            "2": "high"
        }
    }
}"""

BIDS_DATA = (
    'participant_id\tprivacy_level\thandedness\tlanguage'
    '\tdate_of_birth\thighest_degree\tinstruments\r\n'
    'sub-test\t0\t1\tde\t1970-01-01\tn/a\t11,12\r\n'
)


def test_json_schema(attributes, db):
    exporter = attribute_exporters.JSONExporter()
    attributes = Attribute.objects.all()
    assert exporter.get_schema(attributes) == JSON_SCHEMA


def test_json_data(attributes, contact):
    exporter = attribute_exporters.JSONExporter()
    attributes = Attribute.objects.all()
    contact.subject.attributes = ATTRIBUTES
    subjects = [('test', contact.subject)]
    assert exporter.get_data(attributes, subjects) == JSON_DATA


def test_bids_schema(attributes, db):
    exporter = attribute_exporters.BIDSExporter()
    attributes = Attribute.objects.all()
    assert exporter.get_schema(attributes) == BIDS_SCHEMA


def test_bids_data(attributes, contact):
    exporter = attribute_exporters.BIDSExporter()
    attributes = Attribute.objects.all()
    contact.subject.attributes = ATTRIBUTES
    subjects = [('test', contact.subject)]
    assert exporter.get_data(attributes, subjects) == BIDS_DATA
