from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.recruitment.models import ParticipationRequest


def test_search_view(
    client, member, study_in_execution_status, study_in_edit_status, contact_domain
):
    contact1 = mommy.make(Contact, first_name='foo', last_name='bar')
    contact2 = mommy.make(Contact, first_name='asd', last_name='asd')
    contact3 = mommy.make(Contact, first_name='foo', last_name='bar')
    mommy.make(
        ParticipationRequest,
        study=study_in_execution_status,
        subject=contact1.subject,
        status=ParticipationRequest.INVITED,
    )
    # wrong status
    mommy.make(
        ParticipationRequest,
        study=study_in_edit_status,
        subject=contact1.subject,
        status=ParticipationRequest.INVITED,
    )
    # wrong name
    mommy.make(
        ParticipationRequest,
        study=study_in_execution_status,
        subject=contact2.subject,
        status=ParticipationRequest.INVITED,
    )
    # wrong status
    mommy.make(
        ParticipationRequest,
        study=study_in_execution_status,
        subject=contact3.subject,
        status=ParticipationRequest.UNSUITABLE,
    )
    client.force_login(member)
    response = client.get('/execution/search/?first_name=foo&last_name=bar')

    assert response.content.count(b'<li class="my-5">') == 1
