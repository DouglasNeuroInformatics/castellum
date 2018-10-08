import uuid
from itertools import cycle

from django.contrib.messages import get_messages

import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.pseudonyms.models import Pseudonym
from castellum.pseudonyms.models import Subject
from castellum.recruitment.models import ParticipationRequest


def test_post_when_study_has_no_minimal_subject_count_set(client, user, published_study):
    client.force_login(user)
    url = '/recruitment/{}/not-contacted/'.format(published_study.pk)
    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'The minimal number of subjects is not set for this study. ' \
                               'Please, contact the responsible person who can set it up.'


@pytest.mark.django_db
def test_post_when_study_has_zero_subject_count_set(client, user, published_study):

    published_study.min_subjects_count = 0
    published_study.save()
    client.force_login(user)
    url = '/recruitment/{}/not-contacted/'.format(published_study.pk)
    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'This study does not require participants. ' \
                               'Please, contact the responsible person who can set it up.'


@pytest.mark.django_db
def test_post_when_more_then_double_minimal_subject_count(client, user, published_study):

    published_study.min_subjects_count = 2
    published_study.save()

    uuids = [uuid.uuid4() for _ in range(4)]
    mommy.make(Subject, id=1)
    contact_pseudonym = mommy.make(Pseudonym,
                                   subject_id=1,
                                   pseudonym=uuid.uuid4(),
                                   domain=Contact.domain)
    mommy.make(Contact, pseudonym=contact_pseudonym)
    pseudonyms = mommy.make(Pseudonym,
                            subject_id=1,
                            pseudonym=cycle(uuids),
                            domain=published_study.domain,
                            _quantity=4)
    mommy.make(ParticipationRequest,
               study=published_study,
               pseudonym=cycle(pseudonyms),
               _quantity=4)

    client.force_login(user)
    url = '/recruitment/{}/not-contacted/'.format(published_study.pk)

    response = client.post(url)
    assert response.status_code == 200
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == 'Application privacy does not allow you to add more subjects. ' \
                               'Please contact provided subjects before adding new ones.'
