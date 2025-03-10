from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment.statistics import get_statistics
from castellum.subjects.models import Subject


def test_statistics(attributes, study, participation):
    subject = baker.make(Subject, attributes={
        'd1': 1,
        'd3': '1930-01-01',
    })

    with freeze_time('1970-01-01'):
        data = get_statistics([subject])

    assert data == {
        'legend': ['Right (1)', 'Left (0)', 'Ambidextrous (0)', 'Other (0)'],
        'rows': [{
            'label': '<18',
            'values': [0, 0, 0, 0],
        }, {
            'label': '18-25',
            'values': [0, 0, 0, 0],
        }, {
            'label': '26-30',
            'values': [0, 0, 0, 0],
        }, {
            'label': '31-35',
            'values': [0, 0, 0, 0],
        }, {
            'label': '36-40',
            'values': [1, 0, 0, 0],  # participation
        }, {
            'label': '41-45',
            'values': [0, 0, 0, 0],
        }, {
            'label': '46-50',
            'values': [0, 0, 0, 0],
        }, {
            'label': '51-55',
            'values': [0, 0, 0, 0],
        }, {
            'label': '56-60',
            'values': [0, 0, 0, 0],
        }, {
            'label': '61-65',
            'values': [0, 0, 0, 0],
        }, {
            'label': '66-70',
            'values': [0, 0, 0, 0],
        }, {
            'label': '>70',
            'values': [0, 0, 0, 0],
        }, {
            'label': 'Other',
            'values': [0, 0, 0, 0],
        }],
    }
