import pytest

from castellum.contacts.models import TimeSlot


@pytest.mark.unittest
def test_str():
    ts = TimeSlot(hour=12)
    assert "12" == str(ts)
