import pytest
from django.core import mail
from model_bakery import baker

from castellum.recruitment.models import MailBatch
from castellum.subjects.models import Consent


@pytest.mark.smoketest
def test_mail_remind(client, member, study_in_execution_status):
    study_in_execution_status.mail_body = 'test'
    study_in_execution_status.save()
    batch = baker.make(MailBatch, study=study_in_execution_status)

    client.force_login(member)
    response = client.get('/recruitment/{}/mail/{}/remind/'.format(
        study_in_execution_status.pk, batch.pk
    ))
    assert response.status_code == 200

    response = client.post('/recruitment/{}/mail/{}/remind/'.format(
        study_in_execution_status.pk, batch.pk
    ))
    assert response.status_code == 302


def test_mail_remind_sends_mail(
    client, member, study_in_execution_status, participation
):
    study_in_execution_status.mail_body = 'test'
    study_in_execution_status.save()
    baker.make(Consent, subject=participation.subject, _fill_optional=['document'])
    batch = baker.make(MailBatch, study=study_in_execution_status)
    participation.batch = batch
    participation.save()
    participation.subject.contact.email = 'test@example.com'
    participation.subject.contact.save()

    client.force_login(member)
    client.post(f'/recruitment/{study_in_execution_status.pk}/mail/{batch.pk}/remind/')
    assert len(mail.outbox) == 1
