import pytest
from model_bakery import baker

from castellum.pseudonyms import helpers
from castellum.pseudonyms.models import CodingList
from castellum.pseudonyms.models import Pseudonym
from castellum.subjects.models import Subject


@pytest.fixture
def pseudonym():
    subject = baker.make(Subject)
    return baker.make(Pseudonym, subject=subject)


@pytest.mark.django_db
def test_get_pseudonym(pseudonym):
    pseudonym2 = baker.make(Pseudonym, subject=pseudonym.subject)

    result = helpers.get_pseudonym(pseudonym.subject, pseudonym2.coding_list.key)

    assert result == pseudonym2.pseudonym


@pytest.mark.django_db
def test_get_pseudonym_that_does_not_exist(pseudonym):
    another_coding_list = baker.make(CodingList)
    result = helpers.get_pseudonym(pseudonym.subject, another_coding_list)

    new_pseudonym = Pseudonym.objects.get(coding_list__key=another_coding_list)

    assert result == new_pseudonym.pseudonym


@pytest.mark.django_db
def test_delete_pseudonym(pseudonym):
    assert Pseudonym.objects.count() == 1
    assert Pseudonym.objects.filter(subject=None).count() == 0

    helpers.delete_pseudonym(pseudonym.coding_list, pseudonym.pseudonym)

    assert Pseudonym.objects.count() == 1
    assert Pseudonym.objects.filter(subject=None).count() == 1


@pytest.mark.django_db
def test_delete_pseudonym_again(pseudonym):
    assert Pseudonym.objects.count() == 1
    assert Pseudonym.objects.filter(subject=None).count() == 0

    helpers.delete_pseudonym(pseudonym.coding_list, pseudonym.pseudonym)

    assert Pseudonym.objects.count() == 1
    assert Pseudonym.objects.filter(subject=None).count() == 1

    helpers.delete_pseudonym(pseudonym.coding_list, pseudonym.pseudonym)

    assert Pseudonym.objects.count() == 1
    assert Pseudonym.objects.filter(subject=None).count() == 1


@pytest.mark.django_db
def test_delete_pseudonym_multiple():
    pseudonym1 = baker.make(Pseudonym, subject=baker.make(Subject))
    pseudonym2 = baker.make(Pseudonym, subject=baker.make(Subject))

    assert Pseudonym.objects.count() == 2
    assert Pseudonym.objects.filter(subject=None).count() == 0

    helpers.delete_pseudonym(pseudonym1.coding_list, pseudonym1.pseudonym)

    assert Pseudonym.objects.count() == 2
    assert Pseudonym.objects.filter(subject=None).count() == 1

    helpers.delete_pseudonym(pseudonym2.coding_list, pseudonym2.pseudonym)

    assert Pseudonym.objects.count() == 2
    assert Pseudonym.objects.filter(subject=None).count() == 2
