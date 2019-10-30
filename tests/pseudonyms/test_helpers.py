import pytest
from model_mommy import mommy

from castellum.pseudonyms import helpers
from castellum.pseudonyms.models import Pseudonym
from castellum.subjects.models import Subject


@pytest.fixture
def pseudonym():
    return mommy.make(Pseudonym)


@pytest.mark.django_db
def test_get_pseudonym(pseudonym):
    pseudonym2 = mommy.make(Pseudonym, subject=pseudonym.subject)

    result = helpers.get_pseudonym(pseudonym.subject, pseudonym2.domain.key)

    assert result == pseudonym2.pseudonym


@pytest.mark.django_db
def test_get_pseudonym_that_does_not_exist(pseudonym):
    another_domain = helpers.create_domain()
    result = helpers.get_pseudonym(pseudonym.subject, another_domain)

    new_pseudonym = Pseudonym.objects.get(domain__key=another_domain)

    assert result == new_pseudonym.pseudonym


@pytest.mark.django_db
def test_create_pseudonym():
    domain = helpers.create_domain()
    result = helpers.create_pseudonym(domain)

    pseudonym = Pseudonym.objects.get(domain__key=domain)

    assert result == pseudonym.pseudonym
    assert Pseudonym.objects.count() == 1


@pytest.mark.django_db
def test_delete_pseudonym(pseudonym):
    assert Pseudonym.objects.count() == 1

    helpers.delete_pseudonym(pseudonym.domain, pseudonym.pseudonym)

    assert Pseudonym.objects.count() == 0
    assert Subject.objects.filter(id=pseudonym.subject.id).count() == 1
