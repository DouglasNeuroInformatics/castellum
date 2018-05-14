import pytest

from castellum_auth.models import User
from castellum_auth.management.commands.create_sample_superuser import Command


@pytest.mark.django_db
def test_command():
    Command().handle()
    Command().handle()
    assert User.objects.filter(username='admin').exists()
