import pytest
from model_mommy import mommy


@pytest.fixture
def prepared_study():
    return mommy.prepare("studies.Study", pk=1)


@pytest.fixture
def prepared_user():
    return mommy.prepare("castellum_auth.User", pk=1)
