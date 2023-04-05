from datetime import date

import pytest
from django.utils import timezone
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.contacts.models import ContactCreationRequest
from castellum.recruitment.models import ReliabilityEntry
from castellum.subjects.models import Consent
from castellum.subjects.models import Subject


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_attributes_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/attributes/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_maintenance_attributes_list(request, client, user, subject):
    baker.make(Consent, subject=subject, _fill_optional=['document'])
    client.force_login(user)
    url = '/subjects/maintenance/attributes/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


@pytest.mark.django_db
def test_maintenance_attributes_no_underage_subjects(request, client, user):
    contact = baker.make(Contact, date_of_birth=date(2020, 1, 1))
    baker.make(Consent, subject=contact.subject, _fill_optional=['document'])
    contact.subject.attributes = {}
    contact.subject.save()

    with freeze_time('2020-02-02 12:00'):
        client.force_login(user)
        url = '/subjects/maintenance/attributes/'
        response = client.get(url)
        assert response.status_code == 200
        assert response.content.count(b'<li class="table-list-item">') == 0


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_contact_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/contact/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 0


def test_maintenance_contact_not_empty(client, user):
    baker.make(Contact, phone_number='', email='')
    client.force_login(user)
    url = '/subjects/maintenance/contact/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_duplicates_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200


def test_maintenance_duplicates_not_empty(client, user):
    baker.make(
        Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1)
    )
    baker.make(
        Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1)
    )
    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


def test_maintenance_duplicates_no_date_of_birth(client, user):
    baker.make(
        Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1)
    )
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=None)
    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


def test_maintenance_duplicates_both_no_date_of_birth(client, user):
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=None)
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=None)
    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


def test_maintenance_duplicates_different_date_of_birth(client, user):
    baker.make(
        Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1)
    )
    baker.make(
        Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2001, 1, 1)
    )
    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 0


def test_maintenance_duplicates_to_be_deleted(client, user):
    baker.make(
        Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1)
    )
    contact = baker.make(
        Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1)
    )
    contact.subject.to_be_deleted = timezone.now()
    contact.subject.save()

    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 0


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_consent_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/consent/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 0


def test_maintenance_consent_from_before_full_age(client, user):
    contact = baker.make(Contact, date_of_birth=date(2000, 1, 1))

    with freeze_time('2014-01-01'):
        baker.make(
            Consent,
            _fill_optional=['document'],
            subject=contact.subject,
            underage_when_given=True
        )

    with freeze_time('2018-01-01'):
        url = '/subjects/maintenance/consent/'
        client.force_login(user)
        response = client.get(url)

    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_reliability_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/reliability/'
    response = client.get(url)
    assert response.status_code == 200


def test_maintenance_reliability(client, user, subject):
    baker.make(ReliabilityEntry, subject=subject, was_reliable=False)
    baker.make(ReliabilityEntry, subject=subject, was_reliable=False)

    client.force_login(user)
    url = '/subjects/maintenance/reliability/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'"table-list-item"') == 1


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_subjectcreationrequest(
    request, user_fixture, client, user, subject_creation_request
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/subjectcreationrequest/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'"table-list-item"') == 1


def test_maintenance_delete_subjectcreationrequest(
    client, user, subject_creation_request
):
    client.force_login(user)
    url = f'/subjects/subjectcreationrequest/{subject_creation_request.pk}/delete/'
    response = client.post(url)
    subject_creation_request.refresh_from_db()
    assert response.status_code == 302
    assert subject_creation_request.data_is_deleted
    assert not ContactCreationRequest.objects.exists()


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_estranged_subjects_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/estranged-subjects/'
    response = client.get(url)
    assert response.status_code == 200


def test_maintenance_estranged_subjects_doesnt_contain_no_consent(
    client, user, subject
):
    client.force_login(user)
    url = '/subjects/maintenance/estranged-subjects/'
    with freeze_time('2000-01-01 12:00'):
        baker.make(Subject)

    with freeze_time(timezone.now()):
        response = client.get(url)
        assert response.content.count(b'"table-list-item"') == 0


def test_maintenance_estranged_subjects_contains_never_contacted(client, user, subject):
    client.force_login(user)
    url = '/subjects/maintenance/estranged-subjects/'
    with freeze_time('2000-01-01 12:00'):
        subject = baker.make(Subject)
        baker.make(Consent, _fill_optional=['document'], subject=subject)

    with freeze_time(timezone.now()):
        response = client.get(url)
        assert response.content.count(b'"table-list-item"') == 1


def test_maintenance_estranged_subjects_doesnt_contain_blocked(client, user, subject):
    client.force_login(user)
    url = '/subjects/maintenance/estranged-subjects/'
    with freeze_time('2000-01-01 12:00'):
        subject = baker.make(Subject, blocked=True)
        baker.make(Consent, _fill_optional=['document'], subject=subject)

    with freeze_time(timezone.now()):
        response = client.get(url)
        assert response.content.count(b'"table-list-item"') == 0


def test_maintenance_estranged_subjects_doesnt_contain_deceased(client, user, subject):
    client.force_login(user)
    url = '/subjects/maintenance/estranged-subjects/'
    with freeze_time('2000-01-01 12:00'):
        subject = baker.make(Subject, deceased=True)
        baker.make(Consent, _fill_optional=['document'], subject=subject)

    with freeze_time(timezone.now()):
        response = client.get(url)
        assert response.content.count(b'"table-list-item"') == 0
