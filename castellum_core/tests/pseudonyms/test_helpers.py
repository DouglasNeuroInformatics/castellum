import pytest

from pseudonyms.helpers import create_pseudonym
from pseudonyms.helpers import resolve_pseudonym
from pseudonyms.helpers import delete_pseudonym
from pseudonyms.helpers import list_pseudonyms
from pseudonyms.models import Pseudonym


def test_create_fresh(db):
    pseudonym1 = create_pseudonym('foo')
    pseudonym2 = create_pseudonym('foo')
    assert pseudonym1 != pseudonym2


def test_resolve_stable(db):
    pseudonym_foo = create_pseudonym('foo')
    pseudonym_bar1 = resolve_pseudonym('foo', pseudonym_foo, 'bar')
    pseudonym_bar2 = resolve_pseudonym('foo', pseudonym_foo, 'bar')
    assert pseudonym_bar1 == pseudonym_bar2


def test_list(db):
    pseudonym_foo = create_pseudonym('foo')
    resolve_pseudonym('foo', pseudonym_foo, 'bar')
    d = dict(list_pseudonyms('foo', pseudonym_foo))
    assert 'foo' in d
    assert 'bar' in d


def test_delete(db):
    pseudonym_foo = create_pseudonym('foo')
    pseudonym_bar1 = resolve_pseudonym('foo', pseudonym_foo, 'bar')
    delete_pseudonym('bar', pseudonym_bar1)
    pseudonym_bar2 = resolve_pseudonym('foo', pseudonym_foo, 'bar')
    assert pseudonym_bar1 != pseudonym_bar2


def test_delete_related(db):
    pseudonym_foo = create_pseudonym('foo')
    pseudonym_bar1 = resolve_pseudonym('foo', pseudonym_foo, 'bar')
    delete_pseudonym('bar', pseudonym_bar1, delete_related=True)
    with pytest.raises(Pseudonym.DoesNotExist):
        resolve_pseudonym('foo', pseudonym_foo, 'bar')
