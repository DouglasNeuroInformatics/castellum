from django.forms import ValidationError

import pytest
from model_mommy import mommy

from castellum.studies.models import Study


@pytest.mark.unittest
def test_str():
    study = mommy.prepare(Study, name='Study name')
    assert 'Study name' == str(study)


@pytest.mark.unittest
@pytest.mark.parametrize('study_type', [x for x, _ in Study.STUDY_TYPES])
def test_clean_with_data_sensitivity_is_true(study_type):
    study = mommy.prepare(Study, study_type=study_type, data_sensitivity=True)
    assert study.clean() is None


@pytest.mark.unittest
def test_clean_fails_if_type_is_fmri_and_data_sensitivity_is_false():
    study = mommy.prepare(Study, study_type=Study.FMRI, data_sensitivity=False)
    with pytest.raises(ValidationError):
        study.clean()


@pytest.mark.unittest
@pytest.mark.parametrize('study_type', [x for x, _ in Study.STUDY_TYPES if x is not Study.FMRI])
def test_clean_with_not_fmri_studies_and_data_sensitivity_is_false(study_type):
    study = mommy.prepare(Study, study_type=study_type, data_sensitivity=False)
    assert study.clean() is None
