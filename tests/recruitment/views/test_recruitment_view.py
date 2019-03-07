import uuid

from django.contrib.messages import get_messages

import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.pseudonyms.models import Pseudonym
from castellum.pseudonyms.models import Subject
from castellum.recruitment.models import ParticipationRequest


@pytest.mark.django_db
def test_post_when_study_has_zero_subject_count_set(client, member, published_study):

    published_study.min_subjects_count = 0
    published_study.save()
    client.force_login(member)
    url = '/recruitment/{}/not-contacted/'.format(published_study.pk)
    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'This study does not require participants. ' \
                               'Please, contact the responsible person who can set it up.'


@pytest.mark.django_db
def test_post_when_more_then_double_minimal_subject_count(client, member, published_study):

    published_study.min_subjects_count = 2
    published_study.save()

    subject = mommy.make(Subject, id=1)
    contact_pseudonym = mommy.make(Pseudonym,
                                   subject_id=1,
                                   pseudonym=uuid.uuid4())
    mommy.make(Contact, pseudonym=contact_pseudonym)
    mommy.make(ParticipationRequest,
               study=published_study,
               subject=subject,
               _quantity=4)

    client.force_login(member)
    url = '/recruitment/{}/not-contacted/'.format(published_study.pk)

    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Application privacy does not allow you to add more subjects. ' \
                               'Please contact provided subjects before adding new ones.'
