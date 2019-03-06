from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from model_mommy import mommy

from django.urls import reverse

from castellum.castellum_auth.models import User
from castellum.contacts.forms import PreludeForm
from castellum.contacts.models import Contact
from castellum.contacts.models.contact import ContactManager
from castellum.contacts.views import ContactCreatePreludeView


@pytest.fixture
def view():
    return ContactCreatePreludeView()


@pytest.fixture
def data():
    return dict(
        first_name="Anna",
        last_name="Bolika",
        date_of_birth="2000-01-01"
    )


@pytest.fixture
def form(data):
    form = PreludeForm(data)
    form.is_valid()
    return form


@pytest.mark.unittest
@patch.object(ContactManager, "fuzzy_filter")
@patch.object(ContactCreatePreludeView, "render_to_response")
def test_form_valid(render_to_response, fuzzy_filter, view, form, request_factory):
    contacts = mommy.prepare(Contact, _quantity=3)

    view.request = request_factory.post(reverse("contacts:create"))
    view.request.user = mommy.prepare(User)
    fuzzy_filter.return_value = contacts

    expected_called_with = {
        "form": form,
        "query": "?" + urlencode(form.cleaned_data),
        "matches": contacts,
    }
    view.form_valid(form)
    render_to_response.assert_called_with(expected_called_with)
