from django.test import RequestFactory

import pytest


@pytest.fixture
def request_factory():
    return RequestFactory()
