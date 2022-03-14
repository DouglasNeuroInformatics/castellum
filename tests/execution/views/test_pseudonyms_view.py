import pytest
from model_bakery import baker

from castellum.recruitment.models import Participation


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_200(request, client, study, user_fixture):
    participation = baker.make(Participation, study=study, status=Participation.INVITED)
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/execution/{}/{}/pseudonyms/'.format(study.pk, participation.pk))
    assert response.status_code == 200


def test_lists_all_pseudonyms(client, conductor, study):
    participation = baker.make(Participation, study=study, status=Participation.INVITED)
    study.domains.create()
    client.force_login(conductor)
    response = client.get('/execution/{}/{}/pseudonyms/'.format(
        study.pk, participation.pk
    ))
    assert response.status_code == 200
    assert response.content.count(b'<tr') == 2


def test_no_name(client, conductor, study, subject):
    participation = baker.make(
        Participation, subject=subject, study=study, status=Participation.INVITED
    )
    study.domains.create()
    client.force_login(conductor)
    response = client.get('/execution/{}/{}/pseudonyms/'.format(
        study.pk, participation.pk
    ))
    assert subject.contact.last_name not in response.content.decode('utf-8')
