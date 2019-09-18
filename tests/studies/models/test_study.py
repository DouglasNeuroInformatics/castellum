import pytest
from model_mommy import mommy

from castellum.pseudonyms.models import Domain
from castellum.studies.models import Study


@pytest.mark.django_db
def test_study_create_delete_domain():
    start_count = Domain.objects.count()

    study = mommy.make(Study, domain=None)
    assert Domain.objects.count() == start_count + 1

    study.delete()
    assert Domain.objects.count() == start_count
