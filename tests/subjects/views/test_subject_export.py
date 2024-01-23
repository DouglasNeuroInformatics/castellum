import datetime
import re

import pytest
from django.apps import apps
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.contacts.models import Address
from castellum.recruitment.models import ReliabilityEntry
from castellum.studies.models import StudySession
from castellum.subjects.models import Consent

EXCLUDED = [
    'admin.',
    'appointments.Appointment.id',
    'appointments.Appointment.participation',
    'auth.',
    'castellum_auth',
    'contacts.Contact.first_name_phonetic',
    'contacts.Contact.geolocation',
    'contacts.Contact.id',
    'contacts.Contact.last_name_phonetic',
    'contacts.Contact.subject_uuid',
    'contacts.ContactCreationRequest.',
    'contacts.Street.',
    'contenttypes.',
    'geofilters.Geolocation.',
    'gis.',
    'mfa.MFAKey.',
    'broadcast_messages.',
    'pseudonyms.Domain.',
    'pseudonyms.Pseudonym.',
    'recruitment.AttributeCategory.',
    'recruitment.AttributeCategoryTranslation.',
    'recruitment.AttributeChoice.',
    'recruitment.AttributeChoiceTranslation.',
    'recruitment.Attribute.',
    'recruitment.AttributeTranslation.',
    'recruitment.MailBatch.',
    'recruitment.NewsMailBatch.',
    'recruitment.Participation.id',
    'recruitment.Participation.subject',
    'recruitment.ReliabilityEntry.id',
    'recruitment.ReliabilityEntry.subject',
    'recruitment.SubjectFilter.',
    'recruitment.SubjectFilterGroup.',
    'sessions.',
    'studies.',
    'subjects.ConsentDocument.',
    'subjects.Consent.id',
    'subjects.Consent.subject',
    'subjects.ConsentRevision.id',
    'subjects.ConsentRevision.subject',
    'subjects.ExportAnswer.id',
    'subjects.Subject.id',
    'subjects.Subject.to_be_deleted_notified',
    'subjects.Subject.pseudonym',
    'subjects.Subject.uuid',
    'subjects.SubjectCreationRequest.',

    # already covered by other fields (e.g. backrefs)
    'subjects.Subject.consent',
    'subjects.ExportAnswer.',
    'contacts.Address.',
    'recruitment.Participation.appointment',
    'recruitment.Participation.participationconsent',
    'recruitment.ExecutionTag.',
    'subjects.Subject.participation',
    'subjects.Subject.reliabilityentry',
    'subjects.Report.',

    # Skipped because it would impact the privacy of users
    'recruitment.Participation.assigned_recruiter',
    'appointments.Appointment.assigned_conductors',

    # Skipped because it should be included in study data
    'recruitment.ParticipationConsent.',
]


def iter_fields():
    for app in apps.get_app_configs():
        for model in app.get_models():
            for field in model._meta.get_fields():
                s = f'{app.label}.{model._meta.object_name}.{field.name}'
                if all(not s.startswith(pattern) for pattern in EXCLUDED):
                    yield s


def test_subject_export_complete(client, user, participation):
    client.force_login(user)
    subject = participation.subject
    subject.export_requested = datetime.date.today()
    baker.make(Address, contact=subject.contact)
    baker.make(Consent, subject=subject)
    session = baker.make(StudySession)
    participation.study.studysession_set.add(session)
    baker.make(Appointment, participation=participation, session=session)
    baker.make(ReliabilityEntry, subject=subject)
    subject.save()

    response = client.get(f'/subjects/{subject.pk}/export/')

    expected = set(iter_fields())
    actual = {
        s.decode('utf-8')
        for s in re.findall(b'data-fieldname="([^"]*)"', response.content)
    }

    assert actual == expected


@pytest.mark.smoketest
@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    pytest.param('subject_manager', marks=pytest.mark.xfail(strict=True)),
    'data_protection_coordinator',
])
def test_export_200(request, client, user_fixture, subject):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = f'/subjects/{subject.pk}/export/'
    response = client.get(url)
    assert response.status_code == 200


def test_export_requested(client, user, subject):
    subject.export_requested = datetime.date.today()
    subject.save()

    client.force_login(user)
    url = f'/subjects/{subject.pk}/export/'
    response = client.get(url)

    assert response.status_code == 200
    assert b'<h2>Procedural data</h2>' in response.content


def test_export_post(client, user, subject):
    client.force_login(user)
    url = f'/subjects/{subject.pk}/export/'

    client.post(url)
    subject.refresh_from_db()
    assert subject.export_requested

    client.post(url)
    subject.refresh_from_db()
    assert not subject.export_requested
