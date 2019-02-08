import pytest

from django.test import RequestFactory


@pytest.fixture
def authenticated_user(client, user):
    client.force_login(user)


@pytest.fixture
def request_factory():
    return RequestFactory()
