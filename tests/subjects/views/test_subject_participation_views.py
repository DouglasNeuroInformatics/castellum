import pytest
from model_bakery import baker

from castellum.recruitment.models import MailBatch
from castellum.recruitment.models import Participation


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_officer', marks=pytest.mark.xfail(strict=True)),
    'super_subject_manager',
])
def test_list_200(request, client, user_fixture, invited):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get(f'/subjects/{invited.subject.pk}/participations/')
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


def test_recruit_200(client, user, subject):
    client.force_login(user)
    response = client.get(f'/subjects/{subject.pk}/participations/recruit/?q=test')
    assert response.status_code == 200
    assert b'No matching studies found' in response.content


def test_recruit_200_with_study(client, member, subject, study):
    client.force_login(member)
    url = f'/subjects/{subject.pk}/participations/recruit/?q={study.name}'
    response = client.get(url)
    assert response.status_code == 200
    assert b'No matching studies found' not in response.content


def test_add_200(client, user, subject):
    client.force_login(user)
    response = client.get(f'/subjects/{subject.pk}/participations/add/?q=test')
    assert response.status_code == 200
    assert b'No matching studies found' in response.content


def test_add_rm_batch(client, user, subject, study):
    batch = baker.make(MailBatch, study=study)
    baker.make(Participation, study=study, subject=subject, batch=batch)

    client.force_login(user)
    response = client.post(f'/subjects/{subject.pk}/participations/add/', {
        'study': study.pk,
    })
    assert response.status_code == 200

    participation = Participation.objects.get(study=study, subject=subject)
    assert participation.batch is None
