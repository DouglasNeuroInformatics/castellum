import pytest
from django.utils import timezone

from castellum_auth.models import User
from castellum_auth.management.commands.clear_sessions import Command


@pytest.mark.django_db
def test_command(client, user):
    client.force_login(user)
    Command().handle()
    response = client.get('/')
    assert not response.wsgi_request.user.is_authenticated
