import pytest
from model_bakery import baker

from tests.markers import skip_old_migration


@pytest.mark.django_db
@skip_old_migration('0.69')
def test_keep_foreign_key(migrator):
    old_state = migrator.apply_initial_migration(
        ('subjects', '0029_subjectcreationrequest_data_is_deleted')
    )
    Subject = old_state.apps.get_model('subjects', 'Subject')
    Consent = old_state.apps.get_model('subjects', 'Consent')
    subject = baker.make(Subject)
    consent = baker.make(Consent, subject=subject)

    new_state = migrator.apply_tested_migration(
        ('subjects', '0032_subject_uuid_foreign_key')
    )
    Subject = new_state.apps.get_model('subjects', 'Subject')
    Consent = new_state.apps.get_model('subjects', 'Consent')
    subject = Subject.objects.first()
    consent = Consent.objects.first()

    assert consent.subject == subject

    migrator.reset()


@pytest.mark.django_db
@skip_old_migration('0.69')
def test_keep_m2m(migrator):
    old_state = migrator.apply_initial_migration(
        ('subjects', '0029_subjectcreationrequest_data_is_deleted')
    )
    Subject = old_state.apps.get_model('subjects', 'Subject')
    StudyType = old_state.apps.get_model('studies', 'StudyType')
    subject = baker.make(Subject)
    study_type = baker.make(StudyType)
    subject.study_type_disinterest.add(study_type)

    new_state = migrator.apply_tested_migration(
        ('subjects', '0032_subject_uuid_foreign_key')
    )
    Subject = new_state.apps.get_model('subjects', 'Subject')
    StudyType = new_state.apps.get_model('studies', 'StudyType')
    subject = Subject.objects.first()
    study_type = StudyType.objects.first()

    assert subject.study_type_disinterest.count() == 1
    assert subject.study_type_disinterest.get() == study_type

    migrator.reset()
