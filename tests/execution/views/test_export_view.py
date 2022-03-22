from model_bakery import baker

from castellum.pseudonyms.models import CodingList
from castellum.pseudonyms.models import Pseudonym
from castellum.recruitment.models import Participation
from castellum.studies.models import Study


def test_single_coding_list(client, conductor, study_in_execution_status):
    baker.make(CodingList, context=study_in_execution_status)

    client.force_login(conductor)
    url = '/execution/{}/export/'.format(study_in_execution_status.pk)
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/zip'


def test_no_coding_list(client, conductor, study_in_execution_status):
    client.force_login(conductor)
    url = '/execution/{}/export/'.format(study_in_execution_status.pk)
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'
    assert b'All coding lists have been deleted.' in response.content


def test_multi_coding_list(client, conductor, study_in_execution_status):
    baker.make(CodingList, context=study_in_execution_status)
    baker.make(CodingList, context=study_in_execution_status)

    client.force_login(conductor)
    url = '/execution/{}/export/'.format(study_in_execution_status.pk)
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/html; charset=utf-8'


def test_multi_coding_list_given(client, conductor, study_in_execution_status):
    baker.make(Participation, study=study_in_execution_status, status=Participation.INVITED)
    baker.make(CodingList, context=study_in_execution_status)
    coding_list2 = baker.make(CodingList, context=study_in_execution_status)

    client.force_login(conductor)
    url = '/execution/{}/export/?coding_list={}'.format(
        study_in_execution_status.pk, coding_list2.key
    )
    response = client.get(url)

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/zip'

    # use existence of pseudonym as indicator which coding_list was used
    assert coding_list2.pseudonym_set.count() == 1
    assert Pseudonym.objects.count() == 1


def test_multi_coding_list_given_invalid(client, conductor, study_in_execution_status):
    baker.make(CodingList, context=study_in_execution_status)
    baker.make(CodingList, context=study_in_execution_status)

    client.force_login(conductor)
    url = '/execution/{}/export/?coding_list={}'.format(study_in_execution_status.pk, 'invalid')
    response = client.get(url)

    assert response.status_code == 404


def test_multi_coding_list_given_wrong_study(client, conductor, study_in_execution_status):
    study2 = baker.make(Study)
    baker.make(CodingList, context=study_in_execution_status)
    coding_list2 = baker.make(CodingList, context=study_in_execution_status)

    client.force_login(conductor)
    url = '/execution/{}/export/?coding_list={}'.format(study2.pk, coding_list2.key)
    response = client.get(url)

    assert response.status_code == 404
