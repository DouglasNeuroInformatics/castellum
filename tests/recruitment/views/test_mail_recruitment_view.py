from django.core import mail
from django.utils import timezone
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.models import MailBatch
from castellum.recruitment.models import Participation
from castellum.recruitment.views import MailRecruitmentRemindView
from castellum.recruitment.views import MailRecruitmentView
from castellum.studies.models import Study
from castellum.subjects.models import Consent


def test_mail_add_to_study(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        mail_subject='some subject',
        mail_body='some body',
    )
    contact1 = baker.make(Contact, email='example1@example.com')
    contact2 = baker.make(Contact, email='example2@example.com')
    baker.make(Consent, subject=contact1.subject, _fill_optional=['document'])
    baker.make(Consent, subject=contact2.subject, _fill_optional=['document'])

    study.members.add(user)
    view = MailRecruitmentView()
    view.study = study
    participations = view.create_participations(3)

    assert len(participations) == 2
    assert len(mail.outbox) == 2

    Participation.objects.bulk_create(participations)
    assert study.participation_set.count() == 2


def test_legal_representative_mail_add_to_study(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        mail_subject='some subject',
        mail_body='some body',
    )
    contact1 = baker.make(Contact, email='example1@example.com')
    contact2 = baker.make(Contact, legal_representatives=[contact1])
    baker.make(Consent, subject=contact2.subject, _fill_optional=['document'])

    study.members.add(user)
    view = MailRecruitmentView()
    view.study = study
    participations = view.create_participations(3)

    assert len(participations) == 1
    assert len(mail.outbox) == 1

    Participation.objects.bulk_create(participations)
    assert study.participation_set.count() == 1


def test_404_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/mail/')
    assert response.status_code == 404


def test_200_if_study_and_mail_settings(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        mail_subject='some subject',
        mail_body='some body',
    )
    study.members.add(user)
    url = f'/recruitment/{study.pk}/mail/'
    response = client.get(url)
    assert response.status_code == 200
    assert b'id_batch_size' in response.content
    assert b'Mail recruitment has not been set up!' not in response.content


def test_200_if_study_no_mail_settings(client, member, study):
    client.force_login(member)
    url = f'/recruitment/{study.pk}/mail/'
    response = client.get(url)
    assert response.status_code == 200
    assert b'Mail recruitment has not been set up!' in response.content
    assert b'id_batch_size' not in response.content


def test_404_if_draft_study(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EDIT,
        mail_subject='some subject',
        mail_body='some body',
    )
    study.members.add(user)
    url = f'/recruitment/{study.pk}/mail/'
    response = client.get(url)
    assert response.status_code == 404


def test_remind_updates_participations(subject, study, client, user):
    now = timezone.now()
    client.force_login(user)

    subject.contact.email = 'foo@example.com'
    subject.contact.save()
    baker.make(Consent, subject=subject, _fill_optional=['document'])

    batch = baker.make(MailBatch, study=study)
    participation = baker.make(Participation, subject=subject, study=study, batch=batch)

    with freeze_time(now):
        remind_view = MailRecruitmentRemindView()
        remind_view.study = study
        remind_view.send_reminder_mails(batch)

    participation.refresh_from_db()
    assert participation.updated_at == now
