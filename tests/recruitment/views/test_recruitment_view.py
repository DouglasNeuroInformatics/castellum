from django.contrib.messages import get_messages

import pytest
from model_mommy import mommy

from castellum.recruitment.models import ParticipationRequest


@pytest.mark.django_db
def test_post_when_study_has_zero_subject_count_set(client, member, study_in_recruitment_mode):

    study_in_recruitment_mode.min_subjects_count = 0
    study_in_recruitment_mode.save()
    client.force_login(member)
    url = '/recruitment/{}/'.format(study_in_recruitment_mode.pk)
    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'This study does not require participants. ' \
                               'Please, contact the responsible person who can set it up.'


@pytest.mark.django_db
def test_post_when_more_then_double_minimal_subject_count(client,
                                                          member,
                                                          contact,
                                                          study_in_recruitment_mode):

    study_in_recruitment_mode.min_subjects_count = 2
    study_in_recruitment_mode.save()

    mommy.make(ParticipationRequest,
               study=study_in_recruitment_mode,
               subject=contact.subject,
               _quantity=4)

    client.force_login(member)
    url = '/recruitment/{}/'.format(study_in_recruitment_mode.pk)

    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Application privacy does not allow you to add more subjects. ' \
                               'Please contact provided subjects before adding new ones.'
