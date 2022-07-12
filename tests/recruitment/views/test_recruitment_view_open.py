from django.conf import settings
from django.contrib.messages import get_messages

import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.studies.models import Study
from castellum.subjects.models import Consent


def create_subject():
    contact = baker.make(Contact)
    subject = contact.subject
    subject.attributes = {'d1': 1}
    subject.save()
    baker.make(Consent, subject=subject, _fill_optional=['document'])
    return subject


def create_participation(study, status=Participation.NOT_CONTACTED):
    subject = create_subject()
    baker.make(Participation, subject=subject, study=study, status=status)


def test_min_subject_count_is_zero(client, member, study_in_execution_status):
    study_in_execution_status.min_subject_count = 0
    study_in_execution_status.save()

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_status.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == (
        "This study does not require participants. "
        "Please, contact the responsible person who can set it up."
    )
    assert response.status_code == 200


@pytest.mark.parametrize("subject_count", [
    10 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR,
    11 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR,
])
def test_not_contacted_count_is_gte_to_hard_limit(
    client, member, study_in_execution_status, subject_count
):
    study_in_execution_status.min_subject_count = 10
    study_in_execution_status.save()

    for i in range(subject_count):
        create_participation(study_in_execution_status)

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_status.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == (
        "Application privacy does not allow you to add more subjects. "
        "Please contact provided subjects before adding new ones."
    )
    assert response.status_code == 200


@pytest.mark.parametrize("subject_count", [
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT,
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT + 1,
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT - settings.CASTELLUM_RECRUITMENT_BATCH_SIZE + 1,
])
def test_not_contacted_count_is_gte_to_soft_limit(
    client, member, study_in_execution_status, subject_count
):
    study_in_execution_status.min_subject_count = 2 * settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT
    study_in_execution_status.save()

    for i in range(subject_count):
        create_participation(study_in_execution_status)
    for i in range(settings.CASTELLUM_RECRUITMENT_BATCH_SIZE):
        create_subject()

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_status.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == (
        "Such workflow is not intended due to privacy reasons. "
        "Please contact provided subjects before adding new ones."
    )

    assert response.status_code == 200


def test_no_matching_subjects(
    client, member, study_in_execution_status, attribute_description
):
    study_in_execution_status.min_subject_count = 5
    study_in_execution_status.save()

    for i in range(5):
        create_subject()

    subject_filter_group = baker.make(SubjectFilterGroup, study=study_in_execution_status)
    baker.make(
        SubjectFilter,
        group=subject_filter_group,
        description=attribute_description,
        operator="exact",
        value="foo",
    )

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_status.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == "No potential participants could be found for this study."
    assert response.status_code == 200


def test_post_urgent(client, member, study_in_execution_status):
    study_in_execution_status.min_subject_count = 2
    study_in_execution_status.save()

    subject1 = create_subject()
    subject2 = create_subject()
    other_study = baker.make(Study)
    with freeze_time('1970-01-01'):
        baker.make(Participation, status=Participation.INVITED, study=other_study, subject=subject1)

    with freeze_time('1970-02-01'):
        client.force_login(member)
        url = '/recruitment/{}/'.format(study_in_execution_status.pk)
        response = client.post(url, {'submit': 'urgent'})

    assert response.status_code == 200
    assert study_in_execution_status.participation_set.filter(subject=subject1).exists()
    assert not study_in_execution_status.participation_set.filter(subject=subject2).exists()
