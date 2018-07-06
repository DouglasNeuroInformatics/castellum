import pytest

from model_mommy import mommy

from pseudonyms import helpers
from pseudonyms.models import Pseudonym, Subject


@pytest.fixture
def pseudonym():
    return mommy.make(Pseudonym)


@pytest.fixture
def pseudonym2(pseudonym):
    return mommy.make(Pseudonym, subject=pseudonym.subject)


@pytest.mark.django_db
def test_delete_pseudonym(pseudonym, pseudonym2):
    assert 2 == len(Pseudonym.objects.all())

    helpers.delete_pseudonym(pseudonym.domain, pseudonym.pseudonym)

    assert 1 == len(Pseudonym.objects.all())
    assert 1 == len(Subject.objects.filter(id=pseudonym.subject.id))


@pytest.mark.django_db
def test_delete_all_pseudonyms_for_related_subject(pseudonym, pseudonym2):
    assert 2 == len(Pseudonym.objects.all())

    helpers.delete_pseudonym(pseudonym.domain, pseudonym.pseudonym, True)

    assert 0 == len(Pseudonym.objects.all())
    assert 0 == len(Subject.objects.filter(id=pseudonym.subject.id))
