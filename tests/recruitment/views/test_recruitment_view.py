from django.contrib.messages import get_messages

import pytest
from model_bakery import baker

from castellum.recruitment.models import ParticipationRequest


def test_200(client, member, started_study):
    client.force_login(member)
    url = '/recruitment/{}/'.format(started_study.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/')
    assert response.status_code == 404


def test_404_if_study_not_started(client, member, study):
    client.force_login(member)
    url = '/recruitment/{}/'.format(study.pk)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_post_when_study_has_zero_subject_count_set(client, member, started_study):
    started_study.min_subject_count = 0
    started_study.save()
    client.force_login(member)
    url = '/recruitment/{}/'.format(started_study.pk)
    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'This study does not require participants. ' \
                               'Please, contact the responsible person who can set it up.'


@pytest.mark.django_db
def test_post_when_more_then_double_minimal_subject_count(
    client, member, started_study
):
    started_study.min_subject_count = 2
    started_study.save()

    baker.make(ParticipationRequest, study=started_study, _quantity=4)

    client.force_login(member)
    url = '/recruitment/{}/'.format(started_study.pk)

    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Application privacy does not allow you to add more subjects. ' \
                               'Please contact provided subjects before adding new ones.'
