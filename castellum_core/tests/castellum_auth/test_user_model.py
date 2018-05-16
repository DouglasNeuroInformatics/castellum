from django.contrib.auth.models import AbstractUser as DjangoUser


def test_castellum_user_is_django_user(user):
    assert isinstance(user, DjangoUser)
