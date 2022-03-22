from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import CodingList
from castellum.recruitment.models import Participation


def test_apiattributesview(
    client, conductor, study_in_execution_status, subject, attribute_description
):
    study = study_in_execution_status
    study.exportable_attributes.add(attribute_description)
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/attributes/'.format(
        study.pk, coding_list.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert data == {'Handedness': None}


def test_participation_status(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.NOT_CONTACTED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/attributes/'.format(
        study.pk, coding_list.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_privacy_level(client, conductor, study_in_execution_status, subject):
    subject.privacy_level = 2
    subject.save()

    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/attributes/'.format(
        study.pk, coding_list.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 403


def test_unrelated_coding_list(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/attributes/'.format(
        study.pk, coding_list.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404
