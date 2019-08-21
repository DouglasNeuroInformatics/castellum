from django.test import RequestFactory

import pytest
from model_mommy import mommy


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def prepared_study():
    return mommy.prepare("studies.Study", pk=1)


@pytest.fixture
def prepared_user():
    return mommy.prepare("castellum_auth.User", pk=1)
