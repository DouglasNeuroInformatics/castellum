from unittest.mock import patch

from django.urls import reverse
from django.db.models import QuerySet

import pytest


URL = reverse('contacts:index')


def test_get_context_data(client, authenticated_user):
    with patch.object(QuerySet, 'count', return_value=5):
        response = client.get(URL)

    assert "total_number_subjects" in response.context
    assert 5 == response.context["total_number_subjects"]
