import pytest
from freezegun import freeze_time

from django.utils import timezone

from castellum_auth.models import User


@pytest.mark.django_db
@pytest.mark.parametrize('expiration_date,expected', (
    (None, False),
    (timezone.now() - timezone.timedelta(days=10), False),
    (timezone.now() + timezone.timedelta(days=10), True),
))
def test_user_expiration_date(client, expiration_date, expected):
    user = User.objects.create(expiration_date=expiration_date)
    client.force_login(user)
    response = client.get('/')
    assert response.wsgi_request.user.is_authenticated == expected


@pytest.mark.django_db
def test_user_expiration_date_superuser(client):
    user = User.objects.create(expiration_date=None, is_superuser=True)
    client.force_login(user)
    response = client.get('/')
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_auto_logout(client):
    with freeze_time('2018-01-01 12:00:00'):
        future = timezone.now() + timezone.timedelta(days=10)
        user = User.objects.create(expiration_date=future)
        client.force_login(user)
        response = client.get('/ping/')
    with freeze_time('2018-01-01 12:20:00'):
        response = client.get('/')
        assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_auto_logout_ping(client):
    with freeze_time('2018-01-01 12:00:00'):
        future = timezone.now() + timezone.timedelta(days=10)
        user = User.objects.create(expiration_date=future)
        client.force_login(user)
        response = client.get('/ping/')
    with freeze_time('2018-01-01 12:10:00'):
        response = client.get('/ping/')
    with freeze_time('2018-01-01 12:20:00'):
        response = client.get('/')
        assert response.wsgi_request.user.is_authenticated
