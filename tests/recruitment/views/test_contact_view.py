import pytest
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.studies.models import StudySession


@pytest.mark.smoketest
def test_200(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 200


def test_404_if_study_is_not_provided(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/3/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_wrong_study_is_provided(client, member, participation, study):
    client.force_login(member)
    url = f'/recruitment/{study.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 404


def test_404_if_study_in_edit_status(client, member, participation):
    participation.study.status = Study.EDIT
    participation.study.save()

    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.freeze_time('2018-01-01')
def test_post_updated_at(client, member, participation):
    client.force_login(member)
    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
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

    url = f'/recruitment/{participation.study.pk}/{participation.pk}/'
    warning = b'Appointments for this participation have been deleted.'

    response = client.post(url, {
        'status': Participation.INVITED,
    }, follow=True)
    assert warning not in response.content

    response = client.post(url, {
        'status': Participation.UNSUITABLE,
    }, follow=True)
    assert warning in response.content
