import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.subjects.models import Consent


@pytest.mark.smoketest
def test_cleanup_view_200(client, recruiter, study_in_execution_status):
    client.force_login(recruiter)
    response = client.get(f'/recruitment/{study_in_execution_status.pk}/cleanup/')
    assert response.status_code == 200


def test_cleanup_view_all(client, recruiter, study_in_execution_status):
    client.force_login(recruiter)

    participation1 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
    )
    participation2 = baker.make(
        Participation, study=study_in_execution_status, status=Participation.INVITED
    )

    url = f'/recruitment/{study_in_execution_status.pk}/cleanup/'
    client.post(url, {'action': 'all'})

    participation1.refresh_from_db()
    assert participation1.status == Participation.UNSUITABLE
    participation2.refresh_from_db()
    assert participation2.status == Participation.INVITED


def test_cleanup_view_awaiting_response(client, recruiter, study_in_execution_status):
    with freeze_time('1970-01-01'):
        participation1 = baker.make(
            Participation,
            study=study_in_execution_status,
            status=Participation.AWAITING_RESPONSE,
        )
        participation2 = baker.make(
            Participation,
            study=study_in_execution_status,
            status=Participation.NOT_CONTACTED,
        )
    with freeze_time('1970-01-15'):
        participation3 = baker.make(
            Participation,
            study=study_in_execution_status,
            status=Participation.AWAITING_RESPONSE,
        )

    with freeze_time('1970-01-15'):
        client.force_login(recruiter)
        url = f'/recruitment/{study_in_execution_status.pk}/cleanup/'
        client.post(url, {'action': 'awaiting_response'})

    participation1.refresh_from_db()
    assert participation1.status == Participation.UNSUITABLE
    participation2.refresh_from_db()
    assert participation2.status == Participation.NOT_CONTACTED
    participation3.refresh_from_db()
    assert participation3.status == Participation.AWAITING_RESPONSE


def test_cleanup_view_mismatch(
    client, recruiter, study_in_execution_status, attribute
):
    client.force_login(recruiter)

    participation1 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
        subject__attributes={
            attribute.json_key: 1,
        },
    )
    baker.make(Consent, subject=participation1.subject, _fill_optional=['document'])

    participation2 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
        subject__attributes={
            attribute.json_key: 2,
        },
    )
    baker.make(Consent, subject=participation2.subject, _fill_optional=['document'])

    participation3 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
        subject__attributes={},
    )
    baker.make(Consent, subject=participation3.subject, _fill_optional=['document'])

    participation4 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.INVITED,
        subject__attributes={
            attribute.json_key: 2,
        },
    )
    baker.make(Consent, subject=participation4.subject, _fill_optional=['document'])

    participation5 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.FOLLOWUP_APPOINTED,
        subject__attributes={
            attribute.json_key: 2,
        },
    )
    baker.make(Consent, subject=participation5.subject, _fill_optional=['document'])

    participation6 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
        subject__attributes={
            attribute.json_key: 1,
        },
    )

    baker.make(
        SubjectFilter,
        group__study=study_in_execution_status,
        attribute=attribute,
        operator='exact',
        value=1,
    )

    url = f'/recruitment/{study_in_execution_status.pk}/cleanup/'
    client.post(url, {'action': 'mismatch'})

    participation1.refresh_from_db()
    assert participation1.status == Participation.NOT_CONTACTED
    participation2.refresh_from_db()
    assert participation2.status == Participation.UNSUITABLE
    participation3.refresh_from_db()
    assert participation3.status == Participation.NOT_CONTACTED
    participation4.refresh_from_db()
    assert participation4.status == Participation.INVITED
    participation5.refresh_from_db()
    assert participation5.status == Participation.FOLLOWUP_APPOINTED
    participation6.refresh_from_db()
    assert participation6.status == Participation.UNSUITABLE
