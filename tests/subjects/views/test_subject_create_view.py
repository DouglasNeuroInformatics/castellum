from django.urls import reverse

import pytest
from castellum.subjects.views import SubjectCreateView

CONTACT_SEARCH_URL = reverse("subjects:index")
CONTACT_CREATE_URL = reverse("subjects:create")


@pytest.fixture
def view():
    return SubjectCreateView()


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
