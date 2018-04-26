import pytest

from django.contrib.auth.models import AbstractUser as DjangoUser

from castellum_auth.models import User as CastellumUser


@pytest.fixture
def user():
    return CastellumUser()


def test_castellum_user_is_django_user(user):
    assert isinstance(user, DjangoUser)
