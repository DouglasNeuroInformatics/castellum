from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import CodingList
from castellum.recruitment.models import Participation


def test_apivalidateview(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': pseudonym}


def test_normalize_pseudonym(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym.lower()
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': pseudonym}


def test_unrelated_coding_list(client, conductor, study_in_execution_status, subject):
    study = study_in_execution_status
    coding_list = baker.make(CodingList)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 404


def test_ignore_privacylevel(client, conductor, study_in_execution_status, subject):
    subject.privacy_level = 2
    subject.save()

    study = study_in_execution_status
    coding_list = baker.make(CodingList, context=study)
    baker.make(Participation, study=study, subject=subject, status=Participation.INVITED)
    pseudonym = get_pseudonym(subject, coding_list.key)

    url = '/execution/api/studies/{}/coding-lists/{}/{}/'.format(
        study.pk, coding_list.key, pseudonym
    )
    response = client.get(url, HTTP_AUTHORIZATION='token ' + conductor.token)

    assert response.status_code == 200
    assert response.json() == {'pseudonym': pseudonym}
