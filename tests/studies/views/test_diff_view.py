import re

from django.apps import apps

from model_bakery import baker

from castellum.studies.models import StudySession
from castellum.studies.models import StudyTag

EXCLUDED = [
    'admin.',
    'appointments.Appointment.',
    'auth.',
    'castellum_auth.User.',
    'contacts.',
    'contenttypes.',
    'geofilters.Geolocation.',
    'mfa.MFAKey.',
    'pseudonyms.Pseudonym.',
    'recruitment.AttributeCategory.',
    'recruitment.AttributeCategoryTranslation.',
    'recruitment.AttributeChoice.',
    'recruitment.AttributeChoiceTranslation.',
    'recruitment.AttributeDescription.',
    'recruitment.AttributeDescriptionTranslation.',
    'recruitment.MailBatch.',
    'recruitment.NewsMailBatch.',
    'recruitment.Participation.',
    'recruitment.ReliabilityEntry.',
    'recruitment.SubjectFilterGroup.id',
    'recruitment.SubjectFilterGroup.study',
    'sessions.',
    'studies.Resource.',
    'studies.StudyGroup.',
    'studies.Study.id',
    'studies.Study.mailbatch',
    'studies.Study.newsmailbatch',
    'studies.Study.participation',
    'studies.StudyMembership.id',
    'studies.StudyMembership.study',
    'studies.Study.reliabilityentry',
    'studies.StudySession.appointment',
    'studies.StudySession.id',
    'studies.StudySession.study',
    'studies.StudyType.',
    'studies.StudyTypeEventFeed.',
    'studies.StudyTypeTranslation.',
    'subjects.',

    # already covered by other fields (e.g. backrefs)
    'pseudonyms.Domain.',  # 'studies.Study.domains'
    'recruitment.SubjectFilter.',  # recruitment.SubjectFilterGroup.subjectfilter
    'recruitment.ExecutionTag.',  # studies.Study.executiontag
    'studies.Study.members',  # studies.Study.studymembership_set
    'studies.StudyTag.',  # studies.Study.studytag

    # intentionally left out
    'studies.Study.previous_status',
    'studies.Study.snapshot',
    'studies.Study.status',
    'studies.StudySession.domains',
    'studies.Study.is_filter_trial'
]


def iter_fields():
    for app in apps.get_app_configs():
        for model in app.get_models():
            for field in model._meta.get_fields():
                s = '{}.{}.{}'.format(app.label, model._meta.object_name, field.name)
                if all(not s.startswith(pattern) for pattern in EXCLUDED):
                    yield s


def test_study_diff_complete(client, member, study, subject_filter):
    client.force_login(member)

    baker.make(StudySession, study=study)
    baker.make(StudyTag, study=study)

    response = client.get('/studies/{}/diff/'.format(study.pk))

    expected = set(iter_fields())
    actual = {s.decode('utf-8') for s in re.findall(b'data-fieldname="([^"]*)"', response.content)}

    assert actual == expected
