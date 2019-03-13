from unittest.mock import patch

import pytest
from model_mommy import mommy

from django.contrib.auth.models import AbstractUser as DjangoUser

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


@pytest.mark.unittest
@patch.object(User, 'has_perm')
@pytest.mark.parametrize('privacy_level, has_perm_return_value', [
    (2, [True, True]),
    (2, [True, False]),
    (1, [False, True]),
    (0, [False, False]),
])
def test_get_privacy_level(has_perm, privacy_level, has_perm_return_value):
    user = mommy.prepare(User)
    has_perm.side_effect = has_perm_return_value

    assert user.get_privacy_level() == privacy_level
