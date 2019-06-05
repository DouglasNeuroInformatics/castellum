import pytest
from model_mommy import mommy

from django.test import RequestFactory


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def prepared_study():
    return mommy.prepare("studies.Study", pk=1)


@pytest.fixture
def prepared_user():
    return mommy.prepare("castellum_auth.User", pk=1)
