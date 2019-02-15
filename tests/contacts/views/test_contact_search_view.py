from itertools import cycle
from unittest.mock import patch

import pytest
from model_mommy import mommy

from django.urls import reverse
from django.views.generic import ListView

from castellum.castellum_auth.models import User
from castellum.contacts.models import Contact
from castellum.contacts.views import ContactSearchView


@pytest.fixture
def view():
    return ContactSearchView()


@pytest.mark.unittest
@patch.object(ListView, 'get_context_data')
@patch.object(User, "has_privacy_level")
def test_get_context_data(has_privacy_level, get_context_data, view, request_factory):
    user = mommy.prepare(User)
    contacts = mommy.prepare(Contact, privacy_level=cycle([0, 1, 2]), _quantity=3)

    has_privacy_level.side_effect = [True, True, False]
    get_context_data.return_value = dict(object_list=contacts)

    view.request = request_factory.get(reverse('contacts:search'))
    view.request.user = user

    context = view.get_context_data()

    assert "contacts" in context
    assert [(contacts[0], True), (contacts[1], True), (contacts[2], False)] == context["contacts"]
