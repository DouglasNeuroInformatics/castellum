import pytest
from model_bakery import baker


@pytest.mark.unittest
def test_str():
    membership = baker.prepare('studies.StudyMembership',
                               study__name='study_name',
                               user__username='username')
    assert 'study_name:username' == str(membership)
