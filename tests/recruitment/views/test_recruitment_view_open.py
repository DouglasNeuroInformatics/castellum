from django.conf import settings
from django.contrib.messages import get_messages

import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup


def test_min_subject_count_is_zero(client, member, started_study):
    started_study.min_subject_count = 0
    started_study.save()

    client.force_login(member)
    url = "/recruitment/{}/".format(started_study.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == ("This study does not require participants. "
                                "Please, contact the responsible person who can set it up.")
    assert response.status_code == 200


@pytest.mark.parametrize("subject_count", [
    10 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR,
    11 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR,
])
def test_not_contacted_count_is_gte_to_hard_limit(client, member, started_study,
                                                  subject_count):
    started_study.min_subject_count = 10
    started_study.save()

    for i in range(subject_count):
        create_participation_request(started_study)

    client.force_login(member)
    url = "/recruitment/{}/".format(started_study.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == ("Application privacy does not allow you to add more subjects. "
                                "Please contact provided subjects before adding new ones.")
    assert response.status_code == 200


@pytest.mark.parametrize("subject_count", [
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT,
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT + 1,
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT - settings.CASTELLUM_RECRUITMENT_BATCH_SIZE + 1,
])
def test_not_contacted_count_is_gte_to_soft_limit(client, member, started_study, subject_count):
    started_study.min_subject_count = 2 * settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT
    started_study.save()

    for i in range(subject_count):
        create_participation_request(started_study)
    for i in range(settings.CASTELLUM_RECRUITMENT_BATCH_SIZE):
        create_attributeset()

    client.force_login(member)
    url = "/recruitment/{}/".format(started_study.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == ("Such workflow is not intended due to privacy reasons. "
                                "Please contact provided subjects before adding new ones.")

    assert response.status_code == 200


def test_no_matching_attribute_sets(client, member, started_study, attribute_description):
    started_study.min_subject_count = 5
    started_study.save()

    for i in range(5):
        create_participation_request(started_study)

    subject_filter_group = baker.make(SubjectFilterGroup, study=started_study)
    baker.make(SubjectFilter, group=subject_filter_group,
               description=attribute_description, operator="exact", value="left")

    client.force_login(member)
    url = "/recruitment/{}/".format(started_study.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == "No potential participants could be found for this study."
    assert response.status_code == 200


def test_create_revision_on_create(client, member, attributeset, started_study):
    started_study.min_subject_count = 5
    started_study.save()

    client.force_login(member)
    url = "/recruitment/{}/".format(started_study.pk)
    client.post(url)

    assert ParticipationRequestRevision.objects.count() == 1


def create_attributeset():
    contact = baker.make(Contact)
    return baker.make(AttributeSet, data={'d1': 1}, subject=contact.subject)


def create_participation_request(study, status=ParticipationRequest.NOT_CONTACTED):
    attributeset = create_attributeset()
    baker.make(ParticipationRequest, subject=attributeset.subject, study=study, status=status)
