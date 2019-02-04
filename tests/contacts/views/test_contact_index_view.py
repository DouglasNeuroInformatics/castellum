from unittest.mock import patch

from django.urls import reverse
from django.db.models import QuerySet

import pytest


URL = reverse('contacts:index')


@pytest.mark.parametrize('user_fixture', [
    pytest.param('study_coordinator', marks=pytest.mark.xfail(strict=True)),
    pytest.param('recruiter', marks=pytest.mark.xfail(strict=True)),
    'subject_manager',
])
def test_status_code_200(request, client, user_fixture):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get(URL)
    assert 200 == response.status_code


def test_get_context_data(client, authenticated_user):
    with patch.object(QuerySet, 'count', return_value=5):
        response = client.get(URL)

    assert "total_number_subjects" in response.context
    assert 5 == response.context["total_number_subjects"]
