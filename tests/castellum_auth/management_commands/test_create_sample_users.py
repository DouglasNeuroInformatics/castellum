import pytest

from castellum.castellum_auth.management.commands.create_sample_users import Command
from castellum.castellum_auth.models import User


@pytest.mark.django_db
def test_create_admin():
    Command().handle()
    Command().handle()
    assert User.objects.filter(username='admin').exists()
