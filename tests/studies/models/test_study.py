import pytest
from model_bakery import baker

from castellum.pseudonyms.models import Domain
from castellum.studies.models import Study


@pytest.mark.django_db
def test_study_delete_domain():
    start_count = Domain.objects.count()

    study = baker.make(Study)
    baker.make(Domain, context=study)
    assert Domain.objects.count() == start_count + 1

    study.delete()
    assert Domain.objects.count() == start_count
