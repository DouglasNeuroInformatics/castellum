import pytest
from django.utils import timezone
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.data_protection.management.commands.cleanup_dashboards import (
    delete_no_legal_basis,
)
from castellum.data_protection.management.commands.cleanup_dashboards import (
    delete_to_be_deleted,
)
from castellum.data_protection.management.commands.cleanup_dashboards import (
    delete_unreachable,
)
from castellum.subjects.models import Consent
from castellum.subjects.models import Subject


def make_subject(**kwargs):
    contact = baker.make(Contact)
    for key, value in kwargs.items():
        setattr(contact.subject, key, value)
    contact.subject.save()
    return contact.subject


@pytest.mark.django_db
def test_cleanup_dashboards_to_be_deleted(subject):
    subject_to_be_deleted = make_subject(to_be_deleted=timezone.now())

    delete_to_be_deleted()

    assert not Subject.objects.filter(pk=subject_to_be_deleted.pk).exists()
    assert Subject.objects.filter(pk=subject.pk).exists()


@pytest.mark.django_db
def test_cleanup_dashboards_dry_run(subject):
    subject_to_be_deleted = make_subject(to_be_deleted=timezone.now())

    delete_to_be_deleted(dry_run=True)

    assert Subject.objects.filter(pk=subject_to_be_deleted.pk).exists()
    assert Subject.objects.filter(pk=subject.pk).exists()


@pytest.mark.django_db
def test_cleanup_dashboards_unreachable(subject):
    other_contact = baker.make(Contact, email='test@example.com')

    delete_unreachable()

    assert not Subject.objects.filter(pk=subject.pk).exists()
    assert Subject.objects.filter(pk=other_contact.subject.pk).exists()


@pytest.mark.django_db
def test_cleanup_dashboards_no_legal_basis(subject, participation):
    contact_no_legal_basis = baker.make(Contact)
    baker.make(Consent, subject=contact_no_legal_basis.subject)

    delete_no_legal_basis()

    assert not Subject.objects.filter(pk=contact_no_legal_basis.subject.pk).exists()
    assert Subject.objects.filter(pk=subject.pk).exists()
