import pytest
from model_mommy import mommy

from castellum.pseudonyms.models import Pseudonym
from castellum.utils.templatetags.utils import field_names


@pytest.fixture
def pseudonym():
    return mommy.prepare(Pseudonym)


def test_field_names(pseudonym):
    assert ["domain", "id", "pseudonym", "subject"] == sorted(field_names(pseudonym))
