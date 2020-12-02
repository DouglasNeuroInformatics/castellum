import datetime
import re

from django.apps import apps

from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.contacts.models import Address
from castellum.studies.models import StudySession
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument

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
    'contacts.Contact.subject_id',
    'contacts.Street.',
    'contenttypes.',
    'geofilters.Geolocation.',
    'pseudonyms.Domain.',
    'pseudonyms.Pseudonym.',
    'recruitment.AttributeCategory.',
    'recruitment.AttributeCategoryTranslation.',
    'recruitment.AttributeChoice.',
    'recruitment.AttributeChoiceTranslation.',
    'recruitment.AttributeDescription.',
    'recruitment.AttributeDescriptionTranslation.',
    'recruitment.MailBatch.',
    'recruitment.NewsMailBatch.',
    'recruitment.Participation.id',
    'recruitment.Participation.subject',
    'recruitment.SubjectFilter.',
    'recruitment.SubjectFilterGroup.',
    'sessions.',
    'studies.',
    'subjects.ConsentDocument.',
    'subjects.Consent.id',
    'subjects.Consent.subject',
    'subjects.ExportAnswer.id',
    'subjects.Subject.id',
    'subjects.SubjectNote.id',
    'subjects.Subject.to_be_deleted_notified',
    'subjects.Subject.note_difficult_to_understand',
    'subjects.Subject.note_hard_of_hearing',
    'subjects.Subject.note_abusive_language',
    'subjects.Subject.pseudonym',
    'subjects.Subject.slug',
    'subjects.TimeSlot.',

    # already covered by other fields (e.g. backrefs)
    'subjects.SubjectNote.',
    'subjects.Subject.consent',
    'subjects.ExportAnswer.',
    'contacts.Address.',
    'recruitment.Participation.appointment',
    'subjects.Subject.participation',
]


def iter_fields():
    for app in apps.get_app_configs():
        for model in app.get_models():
            for field in model._meta.get_fields():
                s = '%s.%s.%s' % (app.label, model._meta.object_name, field.name)
                if all(not s.startswith(pattern) for pattern in EXCLUDED):
                    yield s


def test_gdpr_export_complete(client, user, participation):
    client.force_login(user)
    subject = participation.subject
    subject.export_requested = datetime.date.today()
    baker.make(Address, contact=subject.contact)
    baker.make(Consent, subject=subject)
    session = baker.make(StudySession)
    participation.study.studysession_set.add(session)
    baker.make(Appointment, participation=participation, session=session)
    subject.save()

    response = client.get('/subjects/%s/export/' % subject.slug)

    expected = set(iter_fields())
    actual = {s.decode('utf-8') for s in re.findall(b'data-fieldname="([^"]*)"', response.content)}

    assert actual == expected
