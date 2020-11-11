from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment.models import Participation


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
