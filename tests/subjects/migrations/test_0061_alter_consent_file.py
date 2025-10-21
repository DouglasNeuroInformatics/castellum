import pytest
from model_bakery import baker

from tests.markers import skip_old_migration


@pytest.mark.django_db(databases=['default', 'contacts'])
@skip_old_migration('26.1')
def test_long_file_name(migrator):
    old_state = migrator.apply_initial_migration(
        ('subjects', '0060_participation_permissions')
    )
    long = 'x' * 90
    Consent = old_state.apps.get_model('subjects', 'Consent')
    baker.make(Consent, file=f'subjects/{long}')

    new_state = migrator.apply_tested_migration(
        ('subjects', '0061_alter_consent_file')
    )

    Consent = new_state.apps.get_model('subjects', 'Consent')
    consent = Consent.objects.first()

    assert consent.file.name == f'subjects/{consent.subject.pk}/{long}'
