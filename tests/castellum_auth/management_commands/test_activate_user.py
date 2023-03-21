import datetime

import pytest
from django.utils import timezone

from castellum.castellum_auth.management.commands.activate_user import Command
from castellum.castellum_auth.models import User


@pytest.mark.django_db
def test_update_expiration_date():
    username = 'test'
    date1 = timezone.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    date2 = timezone.datetime(1970, 1, 2, tzinfo=datetime.timezone.utc)

    Command().handle(username=username, date=date1)
    user = User.objects.get(username=username)
    assert user.expiration_date == date1

    Command().handle(username=username, date=date2)
    user = User.objects.get(username=username)
    assert user.expiration_date == date2


@pytest.mark.django_db
def test_set_unusable_password():
    username = 'test'
    date = timezone.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

    Command().handle(username=username, date=date)
    user = User.objects.get(username=username)
    assert not user.has_usable_password()

    user.set_password('ajsd;lkasd;lkasd')
    user.save()

    Command().handle(username=username, date=date)
    user = User.objects.get(username=username)
    assert user.has_usable_password()


@pytest.mark.unittest
def test_date_arg():
    cmd = Command()
    parser = cmd.create_parser('django-admin', 'activate_user')
    args = parser.parse_args(['test', '1970-01-01'])
    assert args.username == 'test'
    assert args.date.year == 1970
    assert args.date.tzinfo is not None
