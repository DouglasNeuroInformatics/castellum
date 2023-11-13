import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment.models import Participation
from castellum.recruitment.views import RecruitmentView


@pytest.mark.smoketest
def test_200(client, member, study_in_execution_status):
    client.force_login(member)
    url = f'/recruitment/{study_in_execution_status.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/')
    assert response.status_code == 404


def test_404_if_study_in_edit_status(client, member, study_in_edit_status):
    client.force_login(member)
    url = f'/recruitment/{study_in_edit_status.pk}/'
    response = client.get(url)
    assert response.status_code == 404


def test_statistics(attributes, study, participation):
    view = RecruitmentView()
    view.study = study

    baker.make(
        Participation,
        study=study,
        status=Participation.INVITED,
        subject__attributes={
            'd1': 1,
            'd3': '1930-01-01',
        },
    )

    with freeze_time('1970-01-01'):
        data = view._get_statistics()

    assert data == {
        'legend': ['Right', 'Left', 'Ambidextrous', 'Other'],
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
