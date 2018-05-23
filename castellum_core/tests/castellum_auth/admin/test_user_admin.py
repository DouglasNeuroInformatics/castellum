import pytz

from django.utils.timezone import datetime
from freezegun import freeze_time
from model_mommy import mommy

from castellum_auth.admin import expiration_date
from castellum_auth.models import User


def test_no_expiration_date_is_set():
    user = mommy.prepare(User)
    assert expiration_date(user) is None


def test_user_account_is_expired():
    user = mommy.prepare(User, expiration_date=datetime(2010, 1, 1, tzinfo=pytz.UTC))
    assert "1/1/2010 (expired)" == expiration_date(user)


@freeze_time("2018-01-01")
def test_expiration_date_is_today():
    user = mommy.prepare(User, expiration_date=datetime(2018, 1, 1, tzinfo=pytz.UTC))
    assert "1/1/2018 (0 days left)" == expiration_date(user)


@freeze_time("2018-01-01")
def test_expiration_date_is_in_the_future():
    user = mommy.prepare(User, expiration_date=datetime(2019, 1, 1, tzinfo=pytz.UTC))
    assert "1/1/2019 (365 days left)" == expiration_date(user)
