from django.conf import settings
from django.contrib.messages import get_messages

import pytest
from model_mommy import mommy

from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision


def test_min_subjects_count_is_zero(client, member, study_in_execution_mode):
    study_in_execution_mode.min_subjects_count = 0
    study_in_execution_mode.save()

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_mode.pk)
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
def test_not_contacted_count_is_gte_to_hard_limit(client, member, study_in_execution_mode,
                                                  subject_count):
    study_in_execution_mode.min_subjects_count = 10
    study_in_execution_mode.save()

    for i in range(subject_count):
        create_participation_request(study_in_execution_mode)

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_mode.pk)
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
def test_not_contacted_count_is_gte_to_soft_limit(client, member, study_in_execution_mode,
                                                  subject_count):
    study_in_execution_mode.min_subjects_count = 2 * settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT
    study_in_execution_mode.save()

    for i in range(subject_count):
        create_participation_request(study_in_execution_mode)
    for i in range(settings.CASTELLUM_RECRUITMENT_BATCH_SIZE):
        create_attributeset()

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_mode.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == ("Such workflow is not intended due to privacy reasons. "
                                "Please contact provided subjects before adding new ones.")

    assert response.status_code == 200


def test_no_matching_attribute_sets(client, member, study_in_execution_mode,
                                    attribute_description):
    study_in_execution_mode.min_subjects_count = 5
    study_in_execution_mode.save()

    for i in range(5):
        create_participation_request(study_in_execution_mode)

    subject_filter_group = mommy.make('recruitment.SubjectFilterGroup',
                                      study=study_in_execution_mode)
    mommy.make('recruitment.SubjectFilter', group=subject_filter_group,
               description=attribute_description, operator="exact", value="left")

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_mode.pk)
    response = client.post(url)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == "We cannot find participants for this study."
    assert response.status_code == 200


def test_create_revision_on_create(client, member, attributeset, study_in_execution_mode):
    study_in_execution_mode.min_subjects_count = 5
    study_in_execution_mode.save()

    client.force_login(member)
    url = "/recruitment/{}/".format(study_in_execution_mode.pk)
    client.post(url)

    assert ParticipationRequestRevision.objects.count() == 1


def create_attributeset():
    contact = mommy.make('contacts.Contact', pseudonym=None)
    return mommy.make('recruitment.AttributeSet', data={'d1': 1}, subject=contact.subject)


def create_participation_request(study, status=ParticipationRequest.NOT_CONTACTED):
    attributeset = create_attributeset()
    mommy.make(ParticipationRequest, subject=attributeset.subject, study=study, status=status)
