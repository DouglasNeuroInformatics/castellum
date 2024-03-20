import pytest
from django.core import mail
from model_bakery import baker

from castellum.recruitment.models import MailBatch
from castellum.subjects.models import Consent


@pytest.mark.smoketest
def test_mail_remind(client, member, study):
    study.mail_body = 'test'
    study.save()
    batch = baker.make(MailBatch, study=study)

    client.force_login(member)
    url = f'/recruitment/{study.pk}/mail/{batch.pk}/remind/'
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url)
    assert response.status_code == 302


def test_mail_remind_sends_mail(client, member, study, participation):
    study.mail_body = 'test'
    study.save()
    baker.make(Consent, subject=participation.subject, _fill_optional=['document'])
    batch = baker.make(MailBatch, study=study)
    participation.batch = batch
    participation.save()
    participation.subject.contact.email = 'test@example.com'
    participation.subject.contact.save()

    client.force_login(member)
    client.post(f'/recruitment/{study.pk}/mail/{batch.pk}/remind/')
    assert len(mail.outbox) == 1
