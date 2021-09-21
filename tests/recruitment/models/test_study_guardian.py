from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment.models import StudyGuardian


def test_study_guardian_delete_on_rm_guardian(client, user, participation, study):
    guardian = baker.make(Contact)
    participation.subject.contact.guardians.add(guardian)
    baker.make(StudyGuardian, participation=participation, subject=guardian.subject)

    client.force_login(user)
    url = '/subjects/{}/contact/'.format(participation.subject.slug)
    response = client.post(url, {
        'first_name': 'foo',
        'last_name': 'bar',
        'guardians_pane': 'guardians',
        'guardians_remove': [guardian.subject.pk],
    })

    assert response.status_code == 302
    assert not StudyGuardian.objects.exists()


def test_study_guardian_no_delete_on_other_contact_update(client, user, participation, study):
    guardian = baker.make(Contact)
    participation.subject.contact.guardians.add(guardian)
    baker.make(StudyGuardian, participation=participation, subject=guardian.subject)

    client.force_login(user)
    url = '/subjects/{}/contact/'.format(participation.subject.slug)
    response = client.post(url, {
        'first_name': 'foo',
        'last_name': 'bar',
        'guardians_pane': 'guardians',
    })

    assert response.status_code == 302
    assert StudyGuardian.objects.exists()
