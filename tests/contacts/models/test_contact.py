from datetime import date
from datetime import datetime
from itertools import cycle

import pytest
from django.utils import timezone
from model_mommy import mommy

from castellum.contacts.models import Contact


@pytest.mark.freeze_time("2020, 10, 31")
@pytest.mark.parametrize("date_of_birth,age", [
    ((2000, 10, 30), 20),
    ((2000, 10, 31), 20),
    ((2000, 11, 1), 19),
])
def test_age_property(date_of_birth, age):
    contact = mommy.prepare(Contact, date_of_birth=date(*date_of_birth))
    assert contact.age == age


@pytest.mark.freeze_time("2020-10-31")
@pytest.mark.django_db
def test_not_available_until_is_in_the_future():
    not_available_until = timezone.localtime(timezone.make_aware(datetime(2020, 11, 1)))
    contact = mommy.make(Contact, not_available_until=not_available_until)

    assert False is contact.is_available


@pytest.mark.freeze_time("2020-10-31")
@pytest.mark.django_db
def test_contact_is_not_available_at_the_weekend():
    contact = mommy.make(Contact)

    assert False is contact.is_available


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_contact_is_currently_not_available():
    contact = mommy.make(Contact)
    timeslots = mommy.make('contacts.TimeSlot', hour=cycle([10, 11, 12]), _quantity=3)
    contact.availability_tuesday.add(*timeslots)

    assert False is contact.is_available


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_contact_is_available():
    contact = mommy.make(Contact)
    timeslots = mommy.make('contacts.TimeSlot', hour=cycle(range(20)), _quantity=20)
    contact.availability_tuesday.add(*timeslots)

    assert True is contact.is_available


@pytest.mark.parametrize('title,expected', (
    ('Dr.', 'Dr. Max Planck'),
    (None, 'Max Planck'),
))
def test_full_name(title, expected):
    contact = mommy.prepare(Contact, first_name='Max', last_name='Planck', title=title)
    assert contact.full_name == expected
