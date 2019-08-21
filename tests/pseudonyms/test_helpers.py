import pytest
from model_mommy import mommy

from castellum.pseudonyms import helpers
from castellum.pseudonyms.models import Pseudonym
from castellum.subjects.models import Subject


@pytest.fixture
def pseudonym():
    return mommy.make(Pseudonym)


@pytest.fixture
def pseudonym2(pseudonym):
    return mommy.make(Pseudonym, subject=pseudonym.subject)


@pytest.mark.django_db
def test_get_pseudonym(pseudonym, pseudonym2):
    result = helpers.get_pseudonym(pseudonym.subject, pseudonym2.domain)

    assert result == pseudonym2.pseudonym


@pytest.mark.django_db
def test_get_pseudonym_that_does_not_exist(pseudonym):
    result = helpers.get_pseudonym(pseudonym.subject, "another_domain")

    new_pseudonym = Pseudonym.objects.get(domain="another_domain")

    assert result == new_pseudonym.pseudonym


@pytest.mark.django_db
def test_create_pseudonym():
    result = helpers.create_pseudonym("domain")

    pseudonym = Pseudonym.objects.select_related("subject").get(domain="domain")

    assert result == pseudonym.pseudonym
    assert 1 == len(Pseudonym.objects.all())


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
