import pytest
from model_bakery import baker

from castellum.studies.models import Study
from castellum.utils.templatetags.utils import display


@pytest.mark.unittest
def test_get_attribute():
    study = baker.prepare(Study, name='Test')
    assert display(study, 'name') == 'Test'


@pytest.mark.unittest
def test_get_attribute_display():
    study = baker.prepare(Study, status=Study.DRAFT)
    assert display(study, 'status') == 'Draft'
