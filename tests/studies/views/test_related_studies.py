from model_bakery import baker

from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.studies.models import Study
from castellum.studies.views.recruitment import get_related_studies


def test_related_studies(attribute_description):
    study = baker.make(Study)
    baker.make(
        SubjectFilter,
        group__study=study,
        description=attribute_description,
        operator='exact',
        value=1,
    )

    participation = baker.make(
        Participation,
        status=Participation.INVITED,
        subject__attributes={
            attribute_description.json_key: 1,
        },
    )

    assert participation.study in get_related_studies(study)


def test_related_studies_filter(attribute_description):
    study = baker.make(Study)
    baker.make(
        SubjectFilter,
        group__study=study,
        description=attribute_description,
        operator='exact',
        value=1,
    )

    participation = baker.make(
        Participation,
        status=Participation.INVITED,
        subject__attributes={
            attribute_description.json_key: 2,
        },
    )

    assert participation.study not in get_related_studies(study)
