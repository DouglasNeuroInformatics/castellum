import datetime

from django.utils import timezone

import pytest
from model_bakery import baker

from castellum.subjects.models import AvailabilitySpan
from castellum.subjects.models import Subject


@pytest.mark.freeze_time("2020-10-31")
@pytest.mark.unittest
def test_not_available_until_is_in_the_future():
    not_available_until = timezone.make_aware(datetime.datetime(2020, 11, 1))
    subject = baker.prepare(Subject, not_available_until=not_available_until)

    assert subject.is_available is False


@pytest.mark.freeze_time("2020-10-31")
@pytest.mark.django_db
def test_contact_is_not_available_at_the_weekend():
    subject = baker.make(Subject)

    assert subject.is_available is False


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_contact_is_currently_not_available():
    subject = baker.make(Subject)
    baker.make(
        AvailabilitySpan,
        subject=subject,
        day=AvailabilitySpan.TUESDAY,
        start=datetime.time(10),
        end=datetime.time(13),
    )
    assert subject.is_available is False


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_contact_is_available():
    subject = baker.make(Subject)
    baker.make(
        AvailabilitySpan,
        subject=subject,
        day=AvailabilitySpan.TUESDAY,
        start=datetime.time(0),
        end=datetime.time(20),
    )
    assert subject.is_available is True


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_get_next_available_datetime():
    not_available_until = timezone.localtime(timezone.make_aware(datetime.datetime(2020, 11, 1)))
    subject = baker.make(Subject, not_available_until=not_available_until)
    baker.make(
        AvailabilitySpan,
        subject=subject,
        day=AvailabilitySpan.TUESDAY,
        start=datetime.time(10),
        end=datetime.time(11),
    )

    actual = subject.get_next_available_datetime(not_available_until)
    expected = timezone.make_aware(datetime.datetime(2020, 11, 3, hour=10))

    assert actual == expected


@pytest.mark.freeze_time("2020-10-27 15:00")
@pytest.mark.django_db
def test_get_next_available_datetime_same_day():
    not_available_until = timezone.localtime(
        timezone.make_aware(datetime.datetime(2020, 10, 27, hour=15))
    )
    subject = baker.make(Subject, not_available_until=not_available_until)
    baker.make(
        AvailabilitySpan,
        subject=subject,
        day=AvailabilitySpan.TUESDAY,
        start=datetime.time(15),
        end=datetime.time(16),
    )

    actual = subject.get_next_available_datetime(not_available_until)
    expected = timezone.make_aware(datetime.datetime(2020, 10, 27, hour=15))

    assert actual == expected
