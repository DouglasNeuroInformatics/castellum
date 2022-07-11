from django.conf import settings
from django.core.files.base import ContentFile

import pytest
from model_bakery import baker

from tests.markers import skip_old_migration


@pytest.mark.django_db(databases=['default', 'contacts'])
@skip_old_migration('0.79.0')
def test_migrate_data(migrator):
    old_state = migrator.apply_initial_migration([
        ('subjects', '0040_consentdocument_name'),
    ])
    Subject = old_state.apps.get_model('subjects', 'Subject')

    subject1 = baker.make(Subject)
    subject2 = baker.make(Subject, consent__status='waiting')
    subject3 = baker.make(Subject, consent__status='confirmed')

    new_state = migrator.apply_tested_migration(
        ('subjects', '0042_alter_consent')
    )
    Subject = new_state.apps.get_model('subjects', 'Subject')
    Consent = new_state.apps.get_model('subjects', 'Consent')

    subject1 = Subject.objects.get(pk=subject1.pk)
    assert subject1.consent.document is None
    assert subject1.consent_waiting_since is None

    subject2 = Subject.objects.get(pk=subject2.pk)
    assert not Consent.objects.filter(subject=subject2).exists()
    assert subject2.consent_waiting_since is not None

    subject3 = Subject.objects.get(pk=subject3.pk)
    assert subject3.consent.document is not None
    assert subject3.consent_waiting_since is None
