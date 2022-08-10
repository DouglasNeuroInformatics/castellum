from datetime import datetime

import pytest
import pytz
from freezegun import freeze_time
from model_bakery import baker

from castellum.castellum_auth.admin import expiration_date_repr
from castellum.castellum_auth.models import User


@pytest.mark.unittest
def test_no_expiration_date_is_set():
    user = baker.prepare(User)
    assert expiration_date_repr(user) is None


@pytest.mark.unittest
def test_user_account_is_expired():
    user = baker.prepare(User, expiration_date=datetime(2010, 1, 1, tzinfo=pytz.UTC))
    assert expiration_date_repr(user) == "01/01/2010 (expired)"


@pytest.mark.unittest
@freeze_time("2018-01-01")
def test_expiration_date_is_today():
    user = baker.prepare(User, expiration_date=datetime(2018, 1, 1, tzinfo=pytz.UTC))
    assert expiration_date_repr(user) == "01/01/2018 (0 days left)"


@pytest.mark.unittest
@freeze_time("2018-01-01")
def test_expiration_date_is_in_the_future():
    user = baker.prepare(User, expiration_date=datetime(2019, 1, 1, tzinfo=pytz.UTC))
    assert expiration_date_repr(user) == "01/01/2019 (365 days left)"
