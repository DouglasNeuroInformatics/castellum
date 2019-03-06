import pytest

from model_mommy import mommy


@pytest.mark.unittest
def test_str():
    membership = mommy.prepare('studies.StudyMembership',
                               study__name='study_name',
                               user__username='username')
    assert 'study_name:username' == str(membership)
