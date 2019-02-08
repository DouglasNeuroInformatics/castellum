import pytest

from django.test import RequestFactory
from django.urls import reverse

from castellum.contacts.views import ContactCreateView


CONTACT_CREATE_PRELUDE_URL = reverse("contacts:create")
CONTACT_CREATE_URL = reverse("contacts:create-form")


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def view():
    return ContactCreateView()


@pytest.mark.unittest
def test_get_cancel_url(view, request_factory):
    view.request = request_factory.get(CONTACT_CREATE_URL, {"first_name": "Anna"})
    assert CONTACT_CREATE_PRELUDE_URL + "?first_name=Anna" == view.get_cancel_url()


@pytest.mark.unittest
@pytest.mark.parametrize("initial_data", [
    {},
    dict(first_name="Anna"),
    dict(first_name="Anna", last_name="Bolika"),
    dict(first_name="Anna", last_name="Bolika", date_of_birth="2000-01-01"),
])
def test_get_initial(view, request_factory, initial_data):
    view.request = request_factory.get(CONTACT_CREATE_URL, initial_data)
    assert initial_data == view.get_initial()


@pytest.mark.unittest
@pytest.mark.parametrize("initial_data", [
    dict(birthday="2000-01-01")
])
def test_get_initial_with_unknown_keys(view, request_factory, initial_data):
    view.request = request_factory.get(CONTACT_CREATE_URL, initial_data)
    assert {} == view.get_initial()


@pytest.mark.unittest
def test_get_form_kwargs(view, user, request_factory):
    data = {
        "first_name": "Anna",
        "last_name": "Bolika",
        "date_of_birth": "2000-01-01",
        "gender": "m",
        "privacy_level": "0",
    }
    view.request = request_factory.post(CONTACT_CREATE_URL, data)
    view.request.user = user

    form_kwargs = view.get_form_kwargs()
    assert user == form_kwargs["user"]
