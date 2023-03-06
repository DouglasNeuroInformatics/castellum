import datetime

import pytest
from django.utils import timezone
from freezegun import freeze_time

from castellum.castellum_auth.models import User


@pytest.mark.django_db
@pytest.mark.parametrize('expiration_date,expected', (
    (None, False),
    (timezone.now() - datetime.timedelta(days=10), False),
    (timezone.now() + datetime.timedelta(days=10), True),
))
def test_user_expiration_date(client, expiration_date, expected):
    user = User.objects.create(expiration_date=expiration_date)
    client.force_login(user)
    response = client.get('/')
    assert response.wsgi_request.user.is_authenticated == expected


@pytest.mark.django_db
def test_auto_logout_inactive(client, user):
    with freeze_time('2018-01-01 12:00:00'):
        client.force_login(user)
        response = client.get('/ping/')
    with freeze_time('2018-01-01 12:20:00'):
        response = client.get('/')
        assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_auto_logout_other_day(client, user):
    with freeze_time('2018-01-01 23:59:59'):
        client.force_login(user)
        response = client.get('/ping/')
    with freeze_time('2018-01-02 00:00:01'):
        response = client.get('/')
        assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_auto_logout_ping(client, user):
    with freeze_time('2018-01-01 12:00:00'):
        client.force_login(user)
        response = client.get('/ping/')
    with freeze_time('2018-01-01 12:10:00'):
        response = client.get('/ping/')
    with freeze_time('2018-01-01 12:20:00'):
        response = client.get('/')
        assert response.wsgi_request.user.is_authenticated


@pytest.mark.parametrize('language,expected', (
    ('de', b'lang="de"'),
    ('en', b'lang="en"'),
))
def test_user_language_middleware(client, user, language, expected):
    user.language = language
    user.save()
    client.force_login(user)
    response = client.get('/')
    assert expected in response.content
