import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.models import ParticipationRequest


@pytest.mark.parametrize('user_fixture', [
    'study_coordinator',
    'recruiter',
    'subject_manager',
    'data_protection_coordinator',
])
def test_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get('/recruitment/search/')
    assert response.status_code == 200


@pytest.mark.parametrize('user_fixture', [
    'member',
    pytest.param('user', marks=pytest.mark.xfail(strict=True)),
])
def test_only_members(request, client, user_fixture, started_study):
    user = request.getfixturevalue(user_fixture)

    contact = baker.make(Contact, first_name='foo', last_name='bar')
    baker.make(ParticipationRequest, study=started_study, subject=contact.subject)

    client.force_login(user)
    response = client.get('/recruitment/search/?search=foo+bar')

    assert response.content.count(b'<li class="my-5">') == 1


def test_search_view(client, member, started_study, study):
    contact1 = baker.make(Contact, first_name='foo', last_name='bar')
    contact2 = baker.make(Contact, first_name='asd', last_name='asd')
    baker.make(ParticipationRequest, study=started_study, subject=contact1.subject)
    baker.make(ParticipationRequest, study=started_study, subject=contact2.subject)
    baker.make(ParticipationRequest, study=study, subject=contact1.subject)
    baker.make(ParticipationRequest, study=study, subject=contact2.subject)

    client.force_login(member)
    response = client.get('/recruitment/search/?search=foo+bar')

    assert response.content.count(b'<li class="my-5">') == 1
