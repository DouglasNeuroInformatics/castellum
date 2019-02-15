import pytest


@pytest.mark.unittest
def test_str(country):
    assert "Germany" == str(country)
