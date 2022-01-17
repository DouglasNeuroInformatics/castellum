import pytest
from model_bakery import baker

from tests.markers import skip_old_migration


@pytest.mark.django_db
@skip_old_migration('0.71')
def test_keep_foreign_key(migrator):
    old_state = migrator.apply_initial_migration([
        ('pseudonyms', '0007_domain_exportable_attributes'),
        ('castellum_auth', '0005_remove_user_logout_timeout'),
    ])
    Domain = old_state.apps.get_model('pseudonyms', 'Domain')
    User = old_state.apps.get_model('castellum_auth', 'User')
    domain = baker.make(Domain)
    user = baker.make(User)
    user.general_domains.add(domain)

    new_state = migrator.apply_tested_migration(
        ('castellum_auth', '0006_remove_user_general_domains')
    )
    Domain = new_state.apps.get_model('pseudonyms', 'Domain')
    User = new_state.apps.get_model('castellum_auth', 'User')
    domain = Domain.objects.first()
    user = User.objects.first()

    assert domain.managers.get() == user

    migrator.reset()
