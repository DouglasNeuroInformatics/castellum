import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_keep_uuid(migrator):
    old_state = migrator.apply_initial_migration(('subjects', '0027_rename_subject_slug_to_uuid'))
    Subject = old_state.apps.get_model('subjects', 'Subject')
    subject = baker.make(Subject)
    uuid = subject.uuid

    new_state = migrator.apply_tested_migration(('subjects', '0028_alter_subject_uuid'))
    Subject = new_state.apps.get_model('subjects', 'Subject')
    subject = Subject.objects.first()

    assert str(subject.uuid) == uuid

    migrator.reset()


@pytest.mark.django_db
def test_many_subjects(migrator):
    old_state = migrator.apply_initial_migration(('subjects', '0027_rename_subject_slug_to_uuid'))
    Subject = old_state.apps.get_model('subjects', 'Subject')
    baker.make(Subject, _quantity=100)

    migrator.apply_tested_migration(('subjects', '0028_alter_subject_uuid'))
    migrator.reset()
