import pytest

from django.forms import ValidationError

from castellum.pseudonyms.generators import md5


@pytest.mark.unittest
def test_clean_generated():
    md5.clean(md5.generate())


@pytest.mark.unittest
def test_clean_invalid_checksum():
    with pytest.raises(ValidationError) as excinfo:
        md5.clean('foo')
    assert 'invalid characters' not in str(excinfo.value)


@pytest.mark.unittest
def test_clean_invalid_chars():
    with pytest.raises(ValidationError) as excinfo:
        md5.clean('ABC!')
    assert 'invalid characters' in str(excinfo.value)


@pytest.mark.unittest
def test_check_denormalized():
    assert md5.clean('vg83END03T') == 'VG83END03T'
    assert md5.clean('VG83ENDO3T') == 'VG83END03T'
