import pytest
from django.utils import timezone

from castellum_auth.models import User


@pytest.fixture
def user(db):
    future = timezone.now() + timezone.timedelta(days=10000)
    return User.objects.create(expiration_date=future)
