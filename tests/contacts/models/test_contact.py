import pytest
from model_bakery import baker

from castellum.contacts.models import Contact


@pytest.mark.unittest
@pytest.mark.parametrize('title,expected', (
    ('Dr.', 'Dr. Max Planck'),
    (None, 'Max Planck'),
))
def test_full_name(title, expected):
    contact = baker.prepare(Contact, first_name='Max', last_name='Planck', title=title)
    assert contact.full_name == expected
