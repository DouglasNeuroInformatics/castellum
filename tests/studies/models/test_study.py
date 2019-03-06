import pytest

from model_mommy import mommy


@pytest.mark.unittest
def test_str():
    study = mommy.prepare('studies.Study', name='Study name')
    assert 'Study name' == str(study)
