import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment.models import Participation
from castellum.recruitment.views import RecruitmentView


@pytest.mark.smoketest
def test_200(client, member, study_in_execution_status):
    client.force_login(member)
    url = '/recruitment/{}/'.format(study_in_execution_status.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/')
    assert response.status_code == 404


def test_404_if_study_in_edit_status(client, member, study_in_edit_status):
    client.force_login(member)
    url = '/recruitment/{}/'.format(study_in_edit_status.pk)
    response = client.get(url)
    assert response.status_code == 404
