from django.core import mail

from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.views import MailRecruitmentView
from castellum.studies.models import Study
from castellum.subjects.models import Consent


def test_mail_add_to_study(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        mail_subject="some subject",
        mail_body="some body",
    )
    contact1 = baker.make(Contact, email="example1@example.com")
    contact2 = baker.make(Contact, email="example2@example.com")
    baker.make(Consent, subject=contact1.subject, status=Consent.CONFIRMED)
    baker.make(Consent, subject=contact2.subject, status=Consent.CONFIRMED)

    study.members.add(user)
    view = MailRecruitmentView()
    view.study = study
    counter = view.create_participations(3)

    assert counter == 2
    assert study.participation_set.count() == 2
    assert len(mail.outbox) == 2


def test_guardian_mail_add_to_study(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        mail_subject="some subject",
        mail_body="some body",
    )
    contact1 = baker.make(Contact, email="example1@example.com")
    contact2 = baker.make(Contact, guardians=[contact1])
    baker.make(Consent, subject=contact2.subject, status=Consent.CONFIRMED)

    study.members.add(user)
    view = MailRecruitmentView()
    view.study = study
    counter = view.create_participations(3)

    assert counter == 1
    assert study.participation_set.count() == 1
    assert len(mail.outbox) == 1


def test_404_if_study_is_not_provided(client, member):
    client.force_login(member)
    response = client.get('/recruitment/3/mail/')
    assert response.status_code == 404


def test_200_if_study_in_execution_status_and_mail_settings(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EXECUTION,
        mail_subject="some subject",
        mail_body="some body",
    )
    study.members.add(user)
    url = '/recruitment/{}/mail/'.format(study.pk)
    response = client.get(url)
    assert response.status_code == 200
    assert b'id_batch_size' in response.content
    assert b'Mail recruitment has not been set up!' not in response.content


def test_200_if_study_in_execution_status_no_mail_settings(
    client, member, study_in_execution_status
):
    client.force_login(member)
    url = '/recruitment/{}/mail/'.format(study_in_execution_status.pk)
    response = client.get(url)
    assert response.status_code == 200
    assert b'Mail recruitment has not been set up!' in response.content
    assert b'id_batch_size' not in response.content


def test_404_if_study_in_edit_status(client, user):
    client.force_login(user)
    study = baker.make(
        Study,
        status=Study.EDIT,
        mail_subject="some subject",
        mail_body="some body",
    )
    study.members.add(user)
    url = '/recruitment/{}/mail/'.format(study.pk)
    response = client.get(url)
    assert response.status_code == 404
