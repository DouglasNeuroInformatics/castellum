import pytest
from model_bakery import baker

from castellum.pseudonyms.models import CodingList
from castellum.studies.models import Study


@pytest.mark.django_db
def test_study_delete_coding_list():
    start_count = CodingList.objects.count()

    study = baker.make(Study)
    baker.make(CodingList, context=study)
    assert CodingList.objects.count() == start_count + 1

    study.delete()
    assert CodingList.objects.count() == start_count
