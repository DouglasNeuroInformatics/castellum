import pytest

from castellum.pseudonyms.generator import check
from castellum.pseudonyms.generator import generate


@pytest.mark.unittest
def test_check_generated():
    assert check(generate())


@pytest.mark.unittest
def test_check_invalid_chars():
    assert not check('foo')


@pytest.mark.unittest
def test_check_denormalized():
    assert check('vg83END03T')
    assert check('VG83ENDO3T')
