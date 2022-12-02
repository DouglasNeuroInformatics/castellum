import pytest
from model_bakery import baker

from castellum.contacts.models import Contact


@pytest.mark.unittest
@pytest.mark.parametrize('title,expected', (
    ('Dr.', 'Dr. Max Planck'),
    (None, 'Max Planck'),
))
def test_full_name(title, expected):
    contact = baker.prepare(Contact, first_name='Max', last_name='Planck', title=title)
    assert contact.full_name == expected


@pytest.mark.django_db
def test_get_legal_representatives_tree():
    contact1 = baker.make(Contact)
    contact2 = baker.make(Contact)
    contact3 = baker.make(Contact)

    contact3.legal_representatives.add(contact1)
    contact3.legal_representatives.add(contact2)

    assert contact3.get_legal_representatives_tree() == [(contact1, []), (contact2, [])]


@pytest.mark.django_db
def test_get_legal_representatives_tree_deep():
    contact1 = baker.make(Contact)
    contact2 = baker.make(Contact)
    contact3 = baker.make(Contact)

    contact2.legal_representatives.add(contact1)
    contact3.legal_representatives.add(contact2)

    assert contact3.get_legal_representatives_tree() == [(contact2, [(contact1, [])])]


@pytest.mark.django_db
def test_get_legal_representatives_tree_circle():
    contact = baker.make(Contact)
    contact.legal_representatives.add(contact)

    assert contact.get_legal_representatives_tree() == []
