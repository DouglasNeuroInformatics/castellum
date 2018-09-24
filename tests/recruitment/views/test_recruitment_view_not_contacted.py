import pytest
from django.conf import settings
from model_mommy import mommy

from castellum.recruitment.models import ParticipationRequest


def test_min_subjects_count_is_none(client, user, published_study):
    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = ("The minimal number of subjects is not set for this study. "
                    "Please, contact the responsible person who can set it up.")

    assert response.status_code == 200
    assert expected_msg in str(response.content)


def test_min_subjects_count_is_zero(client, user, published_study):
    published_study.min_subjects_count = 0
    published_study.save()

    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = ("This study does not require participants. "
                    "Please, contact the responsible person who can set it up.")

    assert response.status_code == 200
    assert expected_msg in str(response.content)


@pytest.mark.parametrize("subject_count", [
    10 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR,
    11 * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR,
])
def test_not_contacted_count_is_gte_to_hard_limit(client, user, published_study, subject_count):
    published_study.min_subjects_count = 10
    published_study.save()

    for i in range(subject_count):
        create_participation_request(published_study)

    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = ("Application privacy does not allow you to add more subjects. "
                    "Please contact provided subjects before adding new ones.")

    assert response.status_code == 200
    assert expected_msg in str(response.content)


@pytest.mark.parametrize("subject_count", [
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT,
    settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT + 1,
])
def test_not_contacted_count_is_gte_to_soft_limit(client, user, published_study, subject_count):
    published_study.min_subjects_count = 2 * settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT
    published_study.save()

    for i in range(subject_count):
        create_participation_request(published_study)

    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = ("Such workflow is not intended due to privacy reasons. "
                    "Please contact provided subjects before adding new ones.")

    assert response.status_code == 200
    assert expected_msg in str(response.content)


def test_no_matching_attribute_sets(client, user, published_study):
    published_study.min_subjects_count = 5
    published_study.save()

    for i in range(5):
        create_participation_request(published_study)

    subject_filter_group = mommy.make('recruitment.SubjectFilterGroup', study=published_study)
    mommy.make('recruitment.SubjectFilter', group=subject_filter_group,
               field_name="handedness", operator="exact", value="left")

    client.force_login(user)
    url = "/recruitment/{}/not-contacted/".format(published_study.pk)
    response = client.post(url)

    expected_msg = "We cannot find participants for this study."

    assert response.status_code == 200
    assert expected_msg in str(response.content)


def create_participation_request(study):
    subject = mommy.make('pseudonyms.Subject')

    contact = mommy.make('contacts.Contact')
    mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["contact"],
               pseudonym=contact.pseudonym)

    attribute_set = mommy.make('recruitment.AttributeSet', handedness='right')
    mommy.make('pseudonyms.Pseudonym', subject=subject, domain=settings.DOMAINS["attributeset"],
               pseudonym=attribute_set.pseudonym)

    participation_request = mommy.make(ParticipationRequest, study=study,
                                       status=ParticipationRequest.NOT_CONTACTED)
    mommy.make('pseudonyms.Pseudonym', subject=subject, domain=study.domain,
               pseudonym=participation_request.pseudonym)
