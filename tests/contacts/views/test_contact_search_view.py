from itertools import cycle
from unittest.mock import patch

from django.urls import reverse
from django.db.models import QuerySet

import pytest
from model_mommy import mommy

from castellum.contacts.models import Contact


URL = reverse('contacts:search')


def test_get_context_data(client, authenticated_user):
    contacts = mommy.prepare(Contact, privacy_level=cycle([0, 1, 2]), _quantity=3)

    # patch __getitem__ because of the pagination
    with patch.object(QuerySet, '__getitem__', return_value=contacts):
        response = client.get(URL)

    assert "contacts" in response.context
    contact1, contact2, contact3 = contacts
    assert [(contact1, True), (contact2, True), (contact3, False)] == response.context["contacts"]
