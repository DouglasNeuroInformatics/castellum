import pytest
import random
from unittest.mock import MagicMock

from django.conf import settings
from django.contrib.messages import get_messages
from model_mommy import mommy
from model_mommy.recipe import Recipe

from castellum.recruitment.models import ParticipationRequest


STUDY_PK = 1

URL = "/recruitment/{}/not-contacted/".format(STUDY_PK)

study_recipe = Recipe(
    'studies.Study',
    pk=STUDY_PK,
    published=True,
    min_subjects_count=5,
)


@pytest.fixture(autouse=True)
def login(client, user):
    client.force_login(user)


def test_min_subjects_count_is_none(client):
    study_recipe.make(min_subjects_count=None)

    expected_message_text = ("The minimal number of subjects is not set for this study. "
                             "Please, contact the responsible person who can set it up.")

    response = client.post(URL)

    assert_message_text(response, expected_message_text)
    assert response.status_code == 200


def test_min_subjects_count_is_zero(client):
    study_recipe.make(min_subjects_count=0)

    expected_message_text = ("This study does not require participants. "
                             "Please, contact the responsible person who can set it up.")

    response = client.post(URL)

    assert_message_text(response, expected_message_text)
    assert response.status_code == 200


@pytest.mark.parametrize("subject_count", [
    5 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR,
    5 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR + 1,
])
def test_not_contacted_count_is_gte_to_hard_limit(client, subject_count):
    study = study_recipe.make()

    for i in range(subject_count):
        create_participation_request(study)

    expected_message_text = ("Application privacy does not allow you to add more subjects. "
                             "Please contact provided subjects before adding new ones.")

    response = client.post(URL)

    assert_message_text(response, expected_message_text)
    assert response.status_code == 200


@pytest.mark.parametrize("subject_count", [
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT,
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT + 1,
])
def test_not_contacted_count_is_gte_to_soft_limit(client, subject_count):
    study = study_recipe.make(min_subjects_count=2*settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT)

    for i in range(subject_count):
        create_participation_request(study)

    expected_message_text = ("Such workflow is not intended due to privacy reasons. "
                             "Please contact provided subjects before adding new ones.")

    response = client.post(URL)

    assert_message_text(response, expected_message_text)
    assert response.status_code == 200


def test_no_matching_attribute_sets(client):
    study = study_recipe.make()

    for i in range(5):
        create_participation_request(study)

    subject_filter_group = mommy.make('recruitment.SubjectFilterGroup', study=study)
    mommy.make('recruitment.SubjectFilter', group=subject_filter_group,
               field_name="handedness", operator="exact", value="left")

    expected_message_text = "We cannot find participants for this study."

    response = client.post(URL)

    assert_message_text(response, expected_message_text)
    assert response.status_code == 200


def test_subject_was_already_contacted(client):
    study = study_recipe.make()

    for i in range(5):
        create_participation_request(study, status=ParticipationRequest.INVITED)
    ParticipationRequest.objects.filter(pk=4).update(status=ParticipationRequest.NOT_CONTACTED)

    subject_filter_group = mommy.make('recruitment.SubjectFilterGroup', study=study)
    mommy.make('recruitment.SubjectFilter', group=subject_filter_group,
               field_name="handedness", operator="exact", value="right")

    random.randint = MagicMock(return_value=4)

    expected_message_text = ("Picked person already participates in the study. You can "
                             "just try again. But this might indicate that there are not "
                             "many matches left.")

    response = client.post(URL)

    assert_message_text(response, expected_message_text)
    assert response.status_code == 200


def test_create_participation_request_for_each_contact_trial(client):
    study = study_recipe.make()

    for i in range(20):
        subject = mommy.make('pseudonyms.Subject')

        contact = mommy.make('contacts.Contact')
        mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["contact"],
                   pseudonym=contact.pseudonym)

        attribute_set = mommy.make('recruitment.AttributeSet', handedness='right')
        mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["attributeset"],
                   pseudonym=attribute_set.pseudonym)

    subject_filter_group = mommy.make('recruitment.SubjectFilterGroup', study=study)
    mommy.make('recruitment.SubjectFilter', group=subject_filter_group,
               field_name="handedness", operator="exact", value="right")

    assert ParticipationRequest.objects.count() == 0

    response = client.post(URL)

    assert ParticipationRequest.objects.count() == 1
    assert response.status_code == 200

    response = client.post(URL)

    assert ParticipationRequest.objects.count() == 2
    assert response.status_code == 200


def test_create_new_participation_request_if_subject_was_not_reached(client):
    study = study_recipe.make()

    for i in range(20):
        subject = mommy.make('pseudonyms.Subject')

        contact = mommy.make('contacts.Contact')
        mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["contact"],
                   pseudonym=contact.pseudonym)

        attribute_set = mommy.make('recruitment.AttributeSet', handedness='right')
        mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["attributeset"],
                   pseudonym=attribute_set.pseudonym)

    subject_filter_group = mommy.make('recruitment.SubjectFilterGroup', study=study)
    mommy.make('recruitment.SubjectFilter', group=subject_filter_group,
               field_name="handedness", operator="exact", value="right")

    participation_request = mommy.make(ParticipationRequest,
                                       status=ParticipationRequest.NOT_REACHED)
    mommy.make('pseudonyms.Pseudonym', subject=subject, domain=study.domain,
               pseudonym=participation_request.pseudonym)

    pseudonym = participation_request.pseudonym

    assert ParticipationRequest.objects.filter(pseudonym=pseudonym).count() == 1

    random.randint = MagicMock(return_value=19)

    response = client.post(URL)

    assert ParticipationRequest.objects.filter(pseudonym=pseudonym).count() == 2
    assert response.status_code == 200


def create_participation_request(study, status=ParticipationRequest.NOT_CONTACTED):
    subject = mommy.make('pseudonyms.Subject')

    contact = mommy.make('contacts.Contact')
    mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["contact"],
               pseudonym=contact.pseudonym)

    attribute_set = mommy.make('recruitment.AttributeSet', handedness='right')
    mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["attributeset"],
               pseudonym=attribute_set.pseudonym)

    participation_request = mommy.make(ParticipationRequest, study=study, status=status)
    mommy.make('pseudonyms.Pseudonym', subject=subject, domain=study.domain,
               pseudonym=participation_request.pseudonym)


def assert_message_text(response, expected_message_text):
    messages = list(get_messages(response.wsgi_request))

    assert len(messages) == 1
    assert str(messages[0]) == expected_message_text
