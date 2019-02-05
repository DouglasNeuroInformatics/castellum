from datetime import date
from itertools import cycle
from unittest.mock import patch

from django.urls import reverse

import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact


URL = reverse('contacts:create')


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


def test_get_request_with_incomplete_params(client, authenticated_user):
    get_params = {'first_name': 'Adre', 'last_name': 'Nalin'}

    response = client.get(URL, get_params)

    assert 200 == response.status_code

    assert get_params == response.context["form"].cleaned_data
    assert {"date_of_birth": ["This field is required."]} == response.context["form"].errors

    assert "query" not in response.context
    assert "matches" not in response.context


def test_get_request_with_complete_params(client, authenticated_user):
    contacts = mommy.prepare(Contact, privacy_level=cycle([0, 1, 2]), _quantity=3)
    get_params = {'first_name': 'Adre', 'last_name': 'Nalin', 'date_of_birth': '2000-01-01'}

    with patch.object(Contact.objects, 'fuzzy_filter', return_value=contacts):
        response = client.get(URL, get_params)

    assert 200 == response.status_code

    expected_data = {'first_name': 'Adre', 'last_name': 'Nalin', 'date_of_birth': date(2000, 1, 1)}
    assert expected_data == response.context["form"].cleaned_data

    assert "query" in response.context

    expected_matches = [(contacts[0], True), (contacts[1], True), (contacts[2], False)]
    assert expected_matches == response.context["matches"]
