from datetime import datetime
from itertools import cycle

import pytest
from django.utils import timezone
from model_mommy import mommy

from castellum.subjects.models import Subject
from castellum.subjects.models import TimeSlot


@pytest.mark.freeze_time("2020-10-31")
@pytest.mark.django_db
def test_not_available_until_is_in_the_future():
    not_available_until = timezone.make_aware(datetime(2020, 11, 1))
    subject = mommy.make(Subject, not_available_until=not_available_until)

    assert False is subject.is_available


@pytest.mark.freeze_time("2020-10-31")
@pytest.mark.django_db
def test_contact_is_not_available_at_the_weekend():
    subject = mommy.make(Subject)

    assert False is subject.is_available


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_contact_is_currently_not_available():
    subject = mommy.make(Subject)
    timeslots = mommy.make(TimeSlot, hour=cycle([10, 11, 12]), _quantity=3)
    subject.availability_tuesday.add(*timeslots)

    assert False is subject.is_available


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_contact_is_available():
    subject = mommy.make(Subject)
    timeslots = mommy.make(TimeSlot, hour=cycle(range(20)), _quantity=20)
    subject.availability_tuesday.add(*timeslots)

    assert True is subject.is_available


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_get_next_available_datetime():
    not_available_until = timezone.localtime(timezone.make_aware(datetime(2020, 11, 1)))
    subject = mommy.make(Subject, not_available_until=not_available_until)
    timeslot = mommy.make(TimeSlot, hour=10)
    subject.availability_tuesday.add(timeslot)

    actual = subject.get_next_available_datetime(not_available_until)
    expected = timezone.make_aware(datetime(2020, 11, 3, hour=10))

    assert actual == expected


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_get_next_available_datetime_same_day():
    not_available_until = timezone.localtime(timezone.make_aware(datetime(2020, 10, 27, hour=15)))
    subject = mommy.make(Subject, not_available_until=not_available_until)
    timeslot = mommy.make(TimeSlot, hour=15)
    subject.availability_tuesday.add(timeslot)

    actual = subject.get_next_available_datetime(not_available_until)
    expected = timezone.make_aware(datetime(2020, 10, 27, hour=15))

    assert actual == expected
