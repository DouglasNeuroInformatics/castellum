from unittest.mock import patch

import pytest
from model_bakery import baker

from castellum.castellum_auth.models import User


@pytest.mark.unittest
@patch.object(User, 'has_perm')
@pytest.mark.parametrize('privacy_level, has_perm_return_value', [
    (2, [True, True]),
    (2, [True, False]),
    (1, [False, True]),
    (0, [False, False]),
])
def test_get_privacy_level(has_perm, privacy_level, has_perm_return_value):
    user = baker.prepare(User)
    has_perm.side_effect = has_perm_return_value

    assert user.get_privacy_level() == privacy_level
