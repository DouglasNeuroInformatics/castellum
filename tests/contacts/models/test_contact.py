from datetime import date

import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact


@pytest.mark.freeze_time("2020, 10, 31")
@pytest.mark.parametrize("birthday,age", [
    ((2000, 10, 30), 20),
    ((2000, 10, 31), 20),
    ((2000, 11, 1), 19),
])
def test_age_property(birthday, age):
    contact = mommy.prepare(Contact, birthday=date(*birthday))
    assert contact.age == age


@pytest.mark.parametrize('title,expected', (
    ('Dr.', 'Dr. Max Planck'),
    (None, 'Max Planck'),
))
def test_full_name(title, expected):
    contact = mommy.prepare(Contact, first_name='Max', last_name='Planck', title=title)
    assert contact.full_name() == expected
