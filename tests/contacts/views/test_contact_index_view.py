from unittest.mock import patch

import pytest

from django.db.models import QuerySet
from django.test import RequestFactory
from django.urls import reverse

from castellum.contacts.views import ContactIndexView


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def view():
    return ContactIndexView()


@pytest.mark.unittest
def test_get_context_data(view, request_factory):
    view.request = request_factory.get(reverse('contacts:index'))

    with patch.object(QuerySet, 'count', return_value=5):
        context = view.get_context_data()

    assert 5 == context["total_number_subjects"]
