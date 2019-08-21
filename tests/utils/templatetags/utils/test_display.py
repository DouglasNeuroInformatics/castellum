import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact
from castellum.utils.templatetags.utils import display


@pytest.fixture
def contact():
    return mommy.prepare(Contact, gender="m", first_name="Max")


def test_get_attribute(contact):
    assert "Max" == display(contact, "first_name")


def test_get_attribute_display(contact):
    assert "male" == display(contact, "gender")
