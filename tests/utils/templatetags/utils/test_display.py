import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.utils.templatetags.utils import display


@pytest.fixture
def contact():
    return baker.prepare(Contact, gender='m', first_name='Max')


@pytest.mark.unittest
def test_get_attribute(contact):
    assert display(contact, 'first_name') == 'Max'


@pytest.mark.unittest
def test_get_attribute_display(contact):
    assert display(contact, 'gender') == 'male'
