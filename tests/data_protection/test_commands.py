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


@pytest.mark.django_db
def test_cleanup_dashboards_to_be_deleted(subject):
    subject_to_be_deleted = baker.make(Subject, to_be_deleted=timezone.now())

    delete_to_be_deleted()

    assert not Subject.objects.filter(pk=subject_to_be_deleted.pk).exists()
    assert Subject.objects.filter(pk=subject.pk).exists()


@pytest.mark.django_db
def test_cleanup_dashboards_unreachable(subject):
    other_contact = baker.make(Contact, email='test@example.com')
    other_subject = other_contact.subject
    other_subject.save()

    delete_unreachable()

    assert not Subject.objects.filter(pk=subject.pk).exists()
    assert Subject.objects.filter(pk=other_subject.pk).exists()


@pytest.mark.django_db
def test_cleanup_dashboards_no_legal_basis(subject, participation):
    contact_no_legal_basis = baker.make(Contact)
    subject_no_legal_basis = contact_no_legal_basis.subject
    baker.make(Consent, subject=subject_no_legal_basis)
    delete_no_legal_basis()

    assert not Subject.objects.filter(pk=subject_no_legal_basis.pk).exists()
    assert Subject.objects.filter(pk=subject.pk).exists()
