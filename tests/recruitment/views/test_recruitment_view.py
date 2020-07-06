from django.contrib.messages import get_messages

import pytest
from model_bakery import baker

from castellum.recruitment.models import Participation


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


@pytest.mark.django_db
def test_post_when_study_has_zero_subject_count_set(client, member, study_in_execution_status):
    study_in_execution_status.min_subject_count = 0
    study_in_execution_status.save()
    client.force_login(member)
    url = '/recruitment/{}/'.format(study_in_execution_status.pk)
    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == (
        'This study does not require participants. '
        'Please, contact the responsible person who can set it up.'
    )


@pytest.mark.django_db
def test_post_when_more_then_double_minimal_subject_count(
    client, member, study_in_execution_status
):
    study_in_execution_status.min_subject_count = 2
    study_in_execution_status.save()

    baker.make(Participation, study=study_in_execution_status, _quantity=4)

    client.force_login(member)
    url = '/recruitment/{}/'.format(study_in_execution_status.pk)

    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == (
        'Application privacy does not allow you to add more subjects. '
        'Please contact provided subjects before adding new ones.'
    )
