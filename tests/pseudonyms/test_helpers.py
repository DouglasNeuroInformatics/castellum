import pytest

from model_mommy import mommy

from castellum.pseudonyms import helpers
from castellum.pseudonyms.models import Pseudonym, Subject


@pytest.fixture
def pseudonym():
    return mommy.make(Pseudonym)


@pytest.fixture
def pseudonym2():
    return mommy.make(Pseudonym)


@pytest.mark.django_db
def test_get_pseudonym(pseudonym):
    result = helpers.get_pseudonym(pseudonym.subject)

    assert result == str(pseudonym.pseudonym)


@pytest.mark.django_db
def test_create_pseudonym():
    result = helpers.create_pseudonym()

    pseudonym = Pseudonym.objects.all().first()

    assert result == str(pseudonym.pseudonym)
    assert 1 == len(Pseudonym.objects.all())


@pytest.mark.django_db
def test_delete_pseudonym(pseudonym, pseudonym2):
    assert 2 == len(Pseudonym.objects.all())

    helpers.delete_pseudonym(pseudonym.pseudonym)

    assert 1 == len(Pseudonym.objects.all())
    assert 1 == len(Subject.objects.filter(id=pseudonym.subject.id))
