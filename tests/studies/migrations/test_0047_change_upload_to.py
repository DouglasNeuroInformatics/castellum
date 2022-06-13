from django.conf import settings
from django.core.files.base import ContentFile

import pytest
from model_bakery import baker

from tests.markers import skip_old_migration


@pytest.mark.django_db(databases=['default', 'contacts'])
@skip_old_migration('0.78.0')
def test_migrate_data(migrator):
    old_state = migrator.apply_initial_migration([
        ('studies', '0046_rename_study_is_onetime_invitation'),
    ])
    Study = old_state.apps.get_model('studies', 'Study')
    study = baker.make(Study)
    study.consent = ContentFile(b'Hello world!', name='test.txt')
    study.save()
    assert (settings.MEDIA_ROOT / 'studies/consent/test.txt').is_file()

    new_state = migrator.apply_tested_migration(
        ('studies', '0047_change_upload_to')
    )
    Study = new_state.apps.get_model('studies', 'Study')
    study = Study.objects.first()

    assert study.consent.url == '/media/studies/{}/consents/test.txt'.format(study.pk)
    assert study.consent.name == 'studies/{}/consents/test.txt'.format(study.pk)

    assert not (settings.MEDIA_ROOT / 'studies/consent/test.txt').exists()
    assert (settings.MEDIA_ROOT / study.consent.name).is_file()

    study.consent.delete()
    migrator.reset()
