import pytest
from django.core import mail

from castellum.recruitment.models import Participation

test_mail = {
    'subject': 'Test Mail',
    'body': 'This is a test.',
}


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    'conductor',
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_news_mail_200(
    request,
    client,
    user_fixture,
    study_in_execution_status,
):
    """
    Only people in charge of conducting studies should be able to see this view.
    """

    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    url = f'/execution/{study_in_execution_status.pk}/news/'
    response = client.get(url)
    assert response.status_code == 200


def test_news_mail_empty_study(client, member, study_in_execution_status):
    """
    For an empty study, no emails should be sent and a warning should pop up if you try.
    """

    assert not study_in_execution_status.participation_set.exists()

    client.force_login(member)

    url = f'/execution/{study_in_execution_status.pk}/news/'
    client.post(url, test_mail, follow='True')

    assert len(mail.outbox) == 0


@pytest.mark.parametrize('interest', [
    pytest.param(Participation.NOT_INTERESTED, marks=pytest.mark.xfail(strict=True)),
    pytest.param(Participation.VIA_POSTAL, marks=pytest.mark.xfail(strict=True)),
    Participation.VIA_EMAIL,
])
def test_news_mail_success(client, member, invited, interest):
    """
    Emails should only successfully send to participants who have expressed interest in
    being updated via email.
    """

    invited.news_interest = interest
    invited.save()

    client.force_login(member)

    url = f'/execution/{invited.study.pk}/news/'
    client.post(url, test_mail, follow='True')

    assert len(mail.outbox) == 1


def test_news_mail_previous_emails(client, member, invited):
    """
    After sending emails, they should show up in the "previous emails" section.
    """
    mail_amount = 4

    invited.news_interest = Participation.VIA_EMAIL
    invited.save()

    client.force_login(member)

    url = f'/execution/{invited.study.pk}/news/'

    for _ in range(mail_amount):
        client.post(url, test_mail, follow='True')

    response = client.get(url)

    assert response.content.count(b'class="table-list-item"') == mail_amount


@pytest.mark.parametrize('content_field', [
    'subject',
    'body',
])
def test_news_mail_empty_content(client, member, invited, content_field):
    """
    If an email has an empty subject or an empty body, it should not be sent.
    """

    invited.news_interest = Participation.VIA_EMAIL
    invited.save()

    client.force_login(member)

    url = f'/execution/{invited.study.pk}/news/'
    empty_subject_mail = {**test_mail, content_field: ''}

    client.post(url, empty_subject_mail, follow='True')

    assert len(mail.outbox) == 0
