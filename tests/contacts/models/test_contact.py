import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact


@pytest.mark.parametrize('title,expected', (
    ('Dr.', 'Dr. Max Planck'),
    (None, 'Max Planck'),
))
def test_full_name(title, expected):
    subject = mommy.prepare(Contact, first_name='Max', last_name='Planck', title=title)
    assert subject.full_name() == expected
