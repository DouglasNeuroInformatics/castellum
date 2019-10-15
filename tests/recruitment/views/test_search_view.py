from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.recruitment.models import ParticipationRequest


def test_search_view(client, member, study_in_execution_mode, study_in_edit_mode):
    contact1 = mommy.make(Contact, first_name='foo', last_name='bar')
    contact2 = mommy.make(Contact, first_name='asd', last_name='asd')
    mommy.make(ParticipationRequest, study=study_in_execution_mode, subject=contact1.subject)
    mommy.make(ParticipationRequest, study=study_in_execution_mode, subject=contact2.subject)
    mommy.make(ParticipationRequest, study=study_in_edit_mode, subject=contact1.subject)
    mommy.make(ParticipationRequest, study=study_in_edit_mode, subject=contact2.subject)

    client.force_login(member)
    response = client.get('/recruitment/search/?first_name=foo&last_name=bar')

    assert response.content.count(b'<li class="my-5">') == 1
