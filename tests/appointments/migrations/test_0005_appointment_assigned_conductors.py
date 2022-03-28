import pytest
from model_bakery import baker

from tests.markers import skip_old_migration


@pytest.mark.django_db(databases=['default', 'contacts'])
@skip_old_migration('0.74')
def test_appointment_assigned_conductors(migrator):
    old_state = migrator.apply_initial_migration(
        ('appointments', '0004_rm_appointments_not_participating')
    )
    Appointment = old_state.apps.get_model('appointments', 'Appointment')
    Participation = old_state.apps.get_model('recruitment', 'Participation')
    Membership = old_state.apps.get_model('studies', 'StudyMembership')
    Study = old_state.apps.get_model('studies', 'Study')

    study = baker.make(Study)
    membership = baker.make(Membership, study=study)
    participation = baker.make(Participation, assigned_conductor=membership, study=study)
    appointment = baker.make(Appointment, participation=participation)

    new_state = migrator.apply_tested_migration(('appointments', '0005_appointment_assigned_conductors'))

    Appointment = new_state.apps.get_model('appointments', 'Appointment')
    Membership = new_state.apps.get_model('studies', 'StudyMembership')

    appointment = Appointment.objects.first()
    membership = Membership.objects.first()

    assert list(appointment.assigned_conductors.all()) == [membership]
    migrator.reset()
