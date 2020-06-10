import pytest
from model_bakery import baker

from castellum.castellum_auth.models import User
from castellum.contacts.models import Contact
from castellum.contacts.routers import APP_LABEL
from castellum.contacts.routers import Router


@pytest.fixture
def router():
    return Router()


@pytest.mark.unittest
@pytest.mark.parametrize("model,expected", [
    (Contact, "contacts"),
    (User, None),
])
def test_db_for_read(router, model, expected):
    assert expected == router.db_for_read(model)


@pytest.mark.unittest
@pytest.mark.parametrize("model,expected", [
    (Contact, "contacts"),
    (User, None),
])
def test_db_for_write(router, model, expected):
    assert expected == router.db_for_write(model)


@pytest.mark.unittest
@pytest.mark.parametrize("db,app_label,expected", [
    (APP_LABEL, APP_LABEL, True),
    ("default", APP_LABEL, False),
    (APP_LABEL, "admin", False),
    ("default", "admin", None),
])
def test_allow_migrate(router, db, app_label, expected):
    assert expected == router.allow_migrate(db, app_label)
