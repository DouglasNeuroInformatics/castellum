import pytest
from model_bakery import baker

from castellum.pseudonyms.models import Pseudonym
from castellum.utils.templatetags.utils import field_names


@pytest.fixture
def pseudonym():
    return baker.prepare(Pseudonym)


def test_field_names(pseudonym):
    assert sorted(field_names(pseudonym)) == ["domain", "id", "pseudonym", "subject"]
