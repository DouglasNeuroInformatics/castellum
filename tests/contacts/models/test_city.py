import pytest


@pytest.mark.unittest
def test_str(city):
    assert "Berlin, Germany" == str(city)
