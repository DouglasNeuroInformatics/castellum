from model_bakery import baker

from castellum.pseudonyms.models import CodingList
from castellum.recruitment.models import Participation


def test_general_coding_list(client, user, conductor, study_in_execution_status, subject):
    coding_list = baker.make(CodingList)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        subject=subject,
        status=Participation.INVITED,
    )

    study_in_execution_status.general_coding_lists.add(coding_list)
    conductor.general_coding_lists.add(coding_list)

    url = '/execution/{}/{}/pseudonyms/{}/'.format(
        study_in_execution_status.pk, participation.pk, coding_list.key
    )
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 200

    participation.delete()

    url = '/subjects/{}/delete/'.format(subject.uuid)
    client.force_login(user)
    response = client.get(url)
    assert b'This subject may still have data in general coding lists.' in response.content


def test_general_coding_list_not_in_study(client, conductor, study_in_execution_status, subject):
    coding_list = baker.make(CodingList)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        subject=subject,
        status=Participation.INVITED,
    )

    conductor.general_coding_lists.add(coding_list)

    url = '/execution/{}/{}/pseudonyms/{}/'.format(
        study_in_execution_status.pk, participation.pk, coding_list.key
    )
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 404


def test_general_coding_list_not_in_user(client, conductor, study_in_execution_status, subject):
    coding_list = baker.make(CodingList)
    participation = baker.make(
        Participation,
        study=study_in_execution_status,
        subject=subject,
        status=Participation.INVITED,
    )

    study_in_execution_status.general_coding_lists.add(coding_list)

    url = '/execution/{}/{}/pseudonyms/{}/'.format(
        study_in_execution_status.pk, participation.pk, coding_list.key
    )
    client.force_login(conductor)
    response = client.get(url)
    assert response.status_code == 404
