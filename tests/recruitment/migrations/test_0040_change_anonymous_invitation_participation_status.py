import pytest
from model_bakery import baker
from tests.markers import skip_old_migration


@pytest.mark.django_db(databases=['default', 'contacts'])
@skip_old_migration('0.73.0')
def test_change_status(migrator):
    old_state = migrator.apply_initial_migration([
        ('recruitment', '0039_subject_uuid_foreign_key'),
        ('studies', '0046_rename_study_is_onetime_invitation'),
    ])
    Study = old_state.apps.get_model('studies', 'Study')
    Participation = old_state.apps.get_model('recruitment', 'Participation')

    EDIT = 1
    FINISHED = 2

    INVITED = 3
    AWAITING_RESPONSE = 5

    study1 = baker.make(Study, is_anonymous_invitation=True, status=EDIT)
    participation1 = baker.make(Participation, study=study1, status=INVITED)

    study2 = baker.make(Study, is_anonymous_invitation=True, status=FINISHED)
    participation2 = baker.make(Participation, study=study2, status=INVITED)

    new_state = migrator.apply_tested_migration(
        ('recruitment', '0040_change_anonymous_invitation_participation_status')
    )
    Participation = new_state.apps.get_model('recruitment', 'Participation')

    participation1 = Participation.objects.filter(pk=participation1.pk).first()
    participation2 = Participation.objects.filter(pk=participation2.pk).first()

    assert participation1.status == AWAITING_RESPONSE
    assert participation2 is None

    migrator.reset()
