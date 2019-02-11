from itertools import cycle
from unittest.mock import patch

import pytest
from model_mommy import mommy

from django.urls import reverse
from django.views.generic import ListView

from castellum.contacts.models import Contact
from castellum.contacts.views import ContactSearchView


@pytest.fixture
def view():
    return ContactSearchView()


@pytest.mark.unittest
def test_get_context_data(view, request_factory, user):
    contacts = mommy.prepare(Contact, privacy_level=cycle([0, 1, 2]), _quantity=3)

    view.request = request_factory.get(reverse('contacts:search'))
    view.request.user = user

    context_data = dict(object_list=contacts)
    with patch.object(ListView, 'get_context_data', return_value=context_data):
        context = view.get_context_data()

    assert "contacts" in context
    assert [(contacts[0], True), (contacts[1], True), (contacts[2], False)] == context["contacts"]
