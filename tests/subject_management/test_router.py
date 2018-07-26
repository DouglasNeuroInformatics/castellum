import pytest

from model_mommy import mommy

from castellum.castellum_auth.models import User
from castellum.subject_management.models import Subject
from castellum.subject_management.routers import APP_LABEL, SubjectManagementRouter


@pytest.fixture
def router():
    return SubjectManagementRouter()


@pytest.mark.parametrize("model,expected", [
    (Subject, "subject_management"),
    (User, None),
])
def test_db_for_read(router, model, expected):
    assert expected == router.db_for_read(model)


@pytest.mark.parametrize("model,expected", [
    (Subject, "subject_management"),
    (User, None),
])
def test_db_for_write(router, model, expected):
    assert expected == router.db_for_write(model)


@pytest.mark.parametrize("obj1,obj2,expected", [
    (mommy.prepare(Subject), mommy.prepare(Subject), True),
    (mommy.prepare(Subject), mommy.prepare(User), None),
    (mommy.prepare(User), mommy.prepare(Subject), None),
    (mommy.prepare(User), mommy.prepare(User), None),
])
def test_allow_relation(router, obj1, obj2, expected):
    assert expected == router.allow_relation(obj1, obj2)


@pytest.mark.parametrize("db,app_label,expected", [
    (APP_LABEL, APP_LABEL, True),
    ("default", APP_LABEL, False),
    (APP_LABEL, "admin", False),
    ("default", "admin", None),
])
def test_allow_migrate(router, db, app_label, expected):
    assert expected == router.allow_migrate(db, app_label)
