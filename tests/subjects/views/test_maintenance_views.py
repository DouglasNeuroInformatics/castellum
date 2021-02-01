from datetime import date

from django.utils import timezone

import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.contacts.models import Contact
from castellum.subjects.models import Consent


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
    baker.make(Consent, subject=subject, status=Consent.CONFIRMED)
    client.force_login(user)
    url = '/subjects/maintenance/attributes/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


@pytest.mark.django_db
def test_maintenance_attributes_no_underage_subjects(request, client, user):
    contact = baker.make(Contact, date_of_birth=date(2020, 1, 1))
    baker.make(Consent, subject=contact.subject, status=Consent.CONFIRMED)
    contact.subject.attributes = {}
    contact.subject.save()
    client.force_login(user)

    with freeze_time("2020-02-02 12:00"):
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
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1))
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1))
    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 1


def test_maintenance_duplicates_different_date_of_birth(client, user):
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1))
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2001, 1, 1))
    client.force_login(user)
    url = '/subjects/maintenance/duplicates/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'<li class="table-list-item">') == 0


def test_maintenance_duplicates_to_be_deleted(client, user):
    baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1))
    contact = baker.make(Contact, first_name='Foo', last_name='Bar', date_of_birth=date(2000, 1, 1))
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


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_waiting_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/waiting/'
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
    pytest.param('data_protection_coordinator', marks=pytest.mark.xfail(strict=True)),
])
def test_maintenance_showup_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = '/subjects/maintenance/showup/'
    response = client.get(url)
    assert response.status_code == 200


def test_maintenance_showup(client, user, participation):
    past = timezone.now()
    baker.make(Appointment, show_up=Appointment.NOSHOW, participation=participation, start=past)
    baker.make(Appointment, show_up=Appointment.NOSHOW, participation=participation, start=past)
    baker.make(Appointment, show_up=Appointment.NOSHOW, participation=participation, start=past)

    client.force_login(user)
    url = '/subjects/maintenance/showup/'
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.count(b'"table-list-item"') == 1
