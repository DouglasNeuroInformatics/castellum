import pytest

from castellum.castellum_auth.management.commands.create_sample_groups import Command
from django.contrib.auth.models import Group


@pytest.mark.django_db
def test_create_sample_groups():
    Command().handle()
    Command().handle()
    assert Group.objects.filter(name="Recruiter").exists()
