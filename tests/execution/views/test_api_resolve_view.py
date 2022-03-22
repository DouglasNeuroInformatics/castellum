from django.utils import timezone

from freezegun import freeze_time
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import CodingList
from castellum.recruitment.models import Participation
from castellum.studies.models import Study


def test_apiresolveview(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)
    target_pseudonym = get_pseudonym(subject, target_coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': target_pseudonym}


def test_token_required(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url)  # no token

    assert response.status_code == 403


def test_user_expired(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    with freeze_time('2000-01-01'):
        conductor.expiration_date = timezone.now()
        conductor.save()

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    with freeze_time('2000-01-02'):
        response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 403


def test_token_required_logged_in(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    client.force_login(conductor)
    response = client.get(url)  # no token

    assert response.status_code == 403


def test_permission_required(client, recruiter, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + recruiter.token)

    assert response.status_code == 403


def test_privacy_level(client, conductor, study_in_execution_status, subject):
    subject.privacy_level = 2
    subject.save()

    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 403


def test_study_status(client, conductor, study, subject):
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_participation_status(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.NOT_CONTACTED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_source_coding_list_wrong_study(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status

    other_study = baker.make(Study)
    coding_list = baker.make(CodingList, context=other_study)

    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_source_coding_list_general(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status

    coding_list = baker.make(CodingList)
    study.general_coding_lists.add(coding_list)
    conductor.general_coding_lists.add(coding_list)

    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_target_coding_list_other_study(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)

    other_study = baker.make(Study)
    target_coding_list = baker.make(CodingList, context=other_study)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_target_coding_list_general(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)

    target_coding_list = baker.make(CodingList)
    study.general_coding_lists.add(target_coding_list)
    conductor.general_coding_lists.add(target_coding_list)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)
    target_pseudonym = get_pseudonym(subject, target_coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': target_pseudonym}


def test_target_coding_list_general_bad_user(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)

    target_coding_list = baker.make(CodingList)
    study.general_coding_lists.add(target_coding_list)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_source_coding_list_general_bad_study(
    client, conductor, study_in_execution_status, subject
):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)

    target_coding_list = baker.make(CodingList)
    conductor.general_coding_lists.add(target_coding_list)

    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym, target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_normalize_pseudonym(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    target_coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)
    target_pseudonym = get_pseudonym(subject, target_coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym.lower(), target_coding_list.key
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': target_pseudonym}
