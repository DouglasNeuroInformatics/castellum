import pytest
from model_mommy import mommy

from castellum.contacts.models import City
from castellum.utils.templatetags.utils import model_verbose_name


@pytest.fixture
def city():
    return mommy.prepare(City)


def test_singular(city):
    assert "City" == model_verbose_name(city)


def test_plural(city):
    assert "Cities" == model_verbose_name(city, plural=True)
