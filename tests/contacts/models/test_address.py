import pytest


@pytest.mark.unittest
def test_str(address):
    assert str(address) == 'Hardenbergplatz 8, 10787 Berlin'


@pytest.mark.unittest
def test_str_with_additional_information(address):
    address.additional_information = 'appartment 3'
    assert str(address) == 'Hardenbergplatz 8 appartment 3, 10787 Berlin'
