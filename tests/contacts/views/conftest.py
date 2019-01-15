import pytest


@pytest.fixture
def authenticated_user(client, user):
    client.force_login(user)
