import pytest

from django.contrib.auth.models import AbstractUser as DjangoUser
from django.utils import timezone

from castellum_auth.models import User


@pytest.mark.django_db
@pytest.mark.parametrize('expiration_date,is_superuser,expected', (
    (None, False, False),
    (timezone.now() - timezone.timedelta(days=10), False, False),
    (timezone.now() + timezone.timedelta(days=10), False, True),
    (None, True, True),
))
def test_user_expiration_date_blank(client, expiration_date, is_superuser, expected):
    user = User(expiration_date=expiration_date, is_superuser=is_superuser)
    user.save()
    client.force_login(user)
    response = client.get('/')
    assert response.wsgi_request.user.is_authenticated == expected
