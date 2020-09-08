import pytest

from castellum.utils import contrast_color


@pytest.mark.unittest
def test_contrast_color():
    assert contrast_color('#0000ff') == '#ffffff'
    assert contrast_color('#ffff00') == '#000000'
