import pytest
from model_bakery import baker
from freezegun import freeze_time
from tests.markers import skip_old_migration


@pytest.mark.django_db
@skip_old_migration('0.70')
def test_keep_uuid(migrator):
    old_state = migrator.apply_initial_migration(('subjects', '0032_subject_uuid_foreign_key'))
    Subject = old_state.apps.get_model('subjects', 'Subject')
    Study = old_state.apps.get_model('studies', 'Study')
    Participation = old_state.apps.get_model('recruitment', 'Participation')
    # re-implementation of constant from model Participation
    INVITED = 3

    with freeze_time("1970-01-01 12:00"):
        subject = baker.make(Subject)
        study = baker.make(Study)
    with freeze_time("2000-01-01 12:00"):
        participation = baker.make(Participation, subject=subject, study=study, status=INVITED)

    new_state = migrator.apply_tested_migration(('subjects', '0033_subject_updated_at'))
    Subject = new_state.apps.get_model('subjects', 'Subject')
    subject = Subject.objects.first()

    assert subject.updated_at == participation.updated_at

    migrator.reset()