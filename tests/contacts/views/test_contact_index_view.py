from unittest.mock import patch

from django.urls import reverse
from django.db.models import QuerySet


URL = reverse('contacts:index')


def test_status_code_200(client, authenticated_user):
    response = client.get(URL)
    assert 200 == response.status_code


def test_get_context_data(client, authenticated_user):
    with patch.object(QuerySet, 'count', return_value=5):
        response = client.get(URL)

    assert "total_number_subjects" in response.context
    assert 5 == response.context["total_number_subjects"]
