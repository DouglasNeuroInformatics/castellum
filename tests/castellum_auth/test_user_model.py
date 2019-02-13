from unittest.mock import patch

import pytest

from django.contrib.auth.models import AbstractUser as DjangoUser
from django.contrib.auth.models import Permission

from castellum.castellum_auth.models import User


def test_castellum_user_is_django_user(user):
    assert isinstance(user, DjangoUser)


@patch('castellum.castellum_auth.models.send_mail')
def test_lock_notification(send_mail, user):
    user.is_active = True
    user.save()
    user = User.objects.get(pk=user.pk)
    send_mail.reset_mock()

    user.is_active = False
    user.save()
    assert send_mail.called


@patch('castellum.castellum_auth.models.send_mail')
def test_unlock_notification(send_mail, user):
    user.is_active = False
    user.save()
    user = User.objects.get(pk=user.pk)
    send_mail.reset_mock()

    user.is_active = True
    user.save()
    assert send_mail.called


def test_get_privacy_level(user):
    permissions = list(Permission.objects.filter(codename__startswith='privacy_level'))
    user.user_permissions.remove(*permissions)

    assert user.get_privacy_level() == 0


@pytest.mark.parametrize("privacy_level", [1, 2])
def test_get_privacy_level_with_level_greater_than_zero(user, privacy_level):
    permission = Permission.objects.get(codename="privacy_level_{}".format(privacy_level))
    user.user_permissions.add(permission)

    assert user.get_privacy_level() == privacy_level
