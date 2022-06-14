import datetime

from django.utils import timezone

import pytest
from freezegun import freeze_time
from model_bakery import baker

from tests.markers import skip_old_migration


@pytest.mark.django_db(databases=['default'])
@skip_old_migration('0.78')
def test_delete_invalid_consentdocuments(migrator):
    old_state = migrator.apply_initial_migration(
        ('subjects', '0037_alter_subject_privacy_level')
    )
    ConsentDocument = old_state.apps.get_model('subjects', 'ConsentDocument')

    now = timezone.now()
    with freeze_time(now):
        baker.make(ConsentDocument, is_valid=False)

    later = timezone.now() + datetime.timedelta(days=7)
    with freeze_time(later):
        baker.make(ConsentDocument, is_valid=True)

    new_state = migrator.apply_tested_migration(
        ('subjects', '0039_remove_consentdocument_is_valid')
    )
    ConsentDocument = new_state.apps.get_model('subjects', 'ConsentDocument')

    assert ConsentDocument.objects.count() == 1
    assert not ConsentDocument.objects.filter(created_at=now).exists()
    assert ConsentDocument.objects.filter(created_at=later).exists()

    migrator.reset()
