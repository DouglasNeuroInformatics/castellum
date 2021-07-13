import pytest
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.studies.models import StudySession


@pytest.mark.smoketest
def test_200(client, member, participation):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation.study.pk, participation.pk)
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member, participation):
    client.force_login(member)
    url = '/recruitment/3/{}/'.format(participation.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_wrong_study_is_provided(client, member, participation, study):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(study.pk, participation.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_study_in_edit_status(client, member, participation):
    participation.study.status = Study.EDIT
    participation.study.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation.study.pk, participation.pk)
    response = client.get(url)
    assert response.status_code == 404


def test_back_to_list(client, member, participation):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation.study.pk, participation.pk)
    response = client.get(url)
    assert response.status_code == 200
    assert b'Back to list' in response.content


def test_back_to_subject(client, member, participation):
    participation.status = 1
    participation.save()

    client.force_login(member)
    url = '/recruitment/{}/{}/?context=subjects:participation-list'.format(
        participation.study.pk, participation.pk
    )
    response = client.get(url)
    assert response.status_code == 200
    assert b'Back to subject' in response.content


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, member, participation):
    client.force_login(member)
    url = '/recruitment/{}/{}/'.format(participation.study.pk, participation.pk)
    client.post(url, {'status': Participation.UNSUITABLE})
    participation = Participation.objects.get()
    assert participation.updated_at.strftime('%Y-%m-%d') == '2018-01-01'


def test_warning_on_appointment_deletion(client, member, participation):
    participation.status = Participation.INVITED
    participation.save()

    session = baker.make(StudySession, study=participation.study, schedule_id='1s2a3')
    baker.make(
        Appointment,
        session=session,
        participation=participation,
    )

    client.force_login(member)

    url = '/recruitment/{}/{}/'.format(participation.study.pk, participation.pk)
    warning = b'Scheduler appointments for this participation have been deleted.'

    response = client.post(url, {
        'status': Participation.INVITED,
    }, follow=True)
    assert warning not in response.content

    response = client.post(url, {
        'status': Participation.UNSUITABLE,
    }, follow=True)
    assert warning in response.content
