from model_bakery import baker

from castellum.pseudonyms.models import CodingList
from castellum.recruitment.models import Participation


def test_apipseudonymsview(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)

    url = '/execution/api/studies/{}/coding-lists/{}/'.format(study.pk, coding_list.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['pseudonyms']) == 1


def test_participation_status(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.NOT_CONTACTED)

    url = '/execution/api/studies/{}/coding-lists/{}/'.format(study.pk, coding_list.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['pseudonyms']) == 0


def test_privacy_level(client, conductor, study_in_execution_status, subject):
    subject.privacy_level = 2
    subject.save()

    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)

    url = '/execution/api/studies/{}/coding-lists/{}/'.format(study.pk, coding_list.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    data = response.json()
    assert len(data['pseudonyms']) == 1


def test_unrelated_coding_list(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)

    url = '/execution/api/studies/{}/coding-lists/{}/'.format(study.pk, coding_list.key)
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404
