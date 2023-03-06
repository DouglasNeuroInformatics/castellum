import pytest
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    'data_protection_coordinator',
])
def test_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/subjects/resolve/')
    assert response.status_code == 200


def test_post(client, user, subject):
    client.force_login(user)

    domain = baker.make(Domain, managers=[user])
    pseudonym = get_pseudonym(subject, domain.key)

    response = client.post('/subjects/resolve/', {
        'domain': domain.key,
        'pseudonym': pseudonym,
    })
    assert response.status_code == 302
    assert response.url == f'/subjects/{subject.pk}/'


def test_only_managers(client, user, subject):
    client.force_login(user)

    domain = baker.make(Domain)
    pseudonym = get_pseudonym(subject, domain.key)

    response = client.post('/subjects/resolve/', {
        'domain': domain.key,
        'pseudonym': pseudonym,
    })
    assert response.status_code == 200
