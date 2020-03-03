from datetime import date

import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.pseudonyms.models import Pseudonym


@pytest.mark.unittest
@pytest.mark.freeze_time("2020, 10, 31")
@pytest.mark.parametrize("date_of_birth,age", [
    ((2000, 10, 30), 20),
    ((2000, 10, 31), 20),
    ((2000, 11, 1), 19),
])
def test_age_property(date_of_birth, age):
    contact = baker.prepare(Contact, date_of_birth=date(*date_of_birth))
    assert contact.age == age


@pytest.mark.unittest
@pytest.mark.parametrize('title,expected', (
    ('Dr.', 'Dr. Max Planck'),
    (None, 'Max Planck'),
))
def test_full_name(title, expected):
    contact = baker.prepare(Contact, first_name='Max', last_name='Planck', title=title)
    assert contact.full_name == expected


@pytest.mark.django_db
def test_contact_create_delete_pseudonym():
    contact = baker.make(Contact)
    subject = contact.subject
    assert Pseudonym.objects.filter(subject=subject).count() == 1

    contact.delete()
    assert Pseudonym.objects.filter(subject=subject).count() == 0
