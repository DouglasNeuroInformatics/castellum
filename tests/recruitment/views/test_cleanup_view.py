import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter


def test_cleanup_view(client, recruiter, study_in_execution_status):
    client.force_login(recruiter)
    participation = baker.make(
        Participation, study=study_in_execution_status, status=Participation.NOT_CONTACTED
    )
    url = '/recruitment/{}/cleanup/'.format(study_in_execution_status.pk)
    client.post(url, {'status': Participation.NOT_CONTACTED})
    participation.refresh_from_db()
    assert participation.status == Participation.UNSUITABLE


def test_cleanup_view_days(client, recruiter, study_in_execution_status):
    client.force_login(recruiter)
    with freeze_time('1970-01-01'):
        participation1 = baker.make(
            Participation, study=study_in_execution_status, status=Participation.NOT_CONTACTED
        )
    with freeze_time('1970-01-15'):
        participation2 = baker.make(
            Participation, study=study_in_execution_status, status=Participation.NOT_CONTACTED
        )
    with freeze_time('1970-01-15'):
        url = '/recruitment/{}/cleanup/'.format(study_in_execution_status.pk)
        client.post(url, {
            'status': Participation.NOT_CONTACTED,
            'days': 5,
        })
    participation1.refresh_from_db()
    assert participation1.status == Participation.UNSUITABLE
    participation2.refresh_from_db()
    assert participation2.status == Participation.NOT_CONTACTED


def test_cleanup_ignore_invited(client, recruiter, study_in_execution_status):
    client.force_login(recruiter)
    with freeze_time('1970-01-01'):
        participation = baker.make(
            Participation, study=study_in_execution_status, status=Participation.INVITED
        )
    with freeze_time('1970-01-15'):
        url = '/recruitment/{}/cleanup/'.format(study_in_execution_status.pk)
        client.post(url, {'days': 5})
    participation.refresh_from_db()
    assert participation.status == Participation.INVITED


@pytest.mark.parametrize('value,status3', [
    ('nomatch', Participation.NOT_CONTACTED),
    ('incomplete', Participation.UNSUITABLE),
])
def test_cleanup_view_match(
    client, recruiter, study_in_execution_status, attribute_description, value, status3
):
    client.force_login(recruiter)

    participation1 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
        subject__attributes={
            attribute_description.json_key: 1,
        },
    )
    participation2 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
        subject__attributes={
            attribute_description.json_key: 2,
        },
    )
    participation3 = baker.make(
        Participation,
        study=study_in_execution_status,
        status=Participation.NOT_CONTACTED,
        subject__attributes={},
    )

    baker.make(
        SubjectFilter,
        group__study=study_in_execution_status,
        description=attribute_description,
        operator='exact',
        value=1,
    )

    url = '/recruitment/{}/cleanup/'.format(study_in_execution_status.pk)
    client.post(url, {'match': value})

    participation1.refresh_from_db()
    assert participation1.status == Participation.NOT_CONTACTED
    participation2.refresh_from_db()
    assert participation2.status == Participation.UNSUITABLE
    participation3.refresh_from_db()
    assert participation3.status == status3
