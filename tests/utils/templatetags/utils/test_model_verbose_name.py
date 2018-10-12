import pytest
from model_mommy import mommy

from castellum.contacts.models import City
from castellum.utils.templatetags.utils import model_verbose_name


@pytest.fixture
def city():
    return mommy.prepare(City)


def test_singular(city):
    assert "city" == model_verbose_name(city)


def test_plural(city):
    assert "cities" == model_verbose_name(city, plural=True)
