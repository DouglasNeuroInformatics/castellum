import pytest

from castellum.subjects.models import TimeSlot


@pytest.mark.unittest
def test_str():
    ts = TimeSlot(hour=12)
    assert "12" == str(ts)
