from unittest.mock import patch

from freezegun import freeze_time
import pytest
from model_mommy import mommy

from castellum.recruitment.models import SubjectFilter
from castellum.recruitment.models import SubjectFilterGroup
from castellum.recruitment.models import AttributeDescription
from castellum.recruitment.models import AttributeCategory
from castellum.recruitment.models import AttributeSet
from castellum.recruitment.models.recruitment import ParticipationRequest
from castellum.recruitment.models.recruitment import ParticipationRequestRevision
from castellum.recruitment.models.attributesets import UNCATEGORIZED
from castellum.studies.models import Study
from castellum.subjects.models import Subject


@pytest.fixture
def study():
    return mommy.make(Study)


@pytest.fixture
def subject_filter_group(study):
    return mommy.make(SubjectFilterGroup, study=study)


@pytest.fixture
def attribute_category():
    return mommy.make(AttributeCategory)


@pytest.mark.django_db
def test_clone_with_empty_filter_group(subject_filter_group, study):
    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 0 == clone.subjectfilter_set.count()


@pytest.mark.django_db
def test_clone_with_multiple_filters(subject_filter_group, attribute_description, study):
    SubjectFilter.objects.create(group=subject_filter_group, description=attribute_description,
                                 operator="operator1", value="value1")
    SubjectFilter.objects.create(group=subject_filter_group, description=attribute_description,
                                 operator="operator2", value="value2")

    clone = SubjectFilterGroup.objects.clone(subject_filter_group)

    assert subject_filter_group.id != clone.id
    assert study == clone.study
    assert 2 == clone.subjectfilter_set.count()


@pytest.mark.django_db
@pytest.mark.freeze_time('2018-01-10')
@patch.object(AttributeDescription.objects, 'get')
@pytest.mark.parametrize('date,bucket', (
    ('1985-01-01', '31-35'),
    ('1982-01-11', '31-35'),
    ('1982-01-10', '36-40'),
    ('1900-01-01', '>70'),
))
def test_attribute_set_get_statistics_bucket_age(get, date, bucket):
    attributeset = mommy.prepare(AttributeSet)
    attributeset.data['d1'] = date

    description = mommy.prepare(AttributeDescription, field_type='AgeField', pk=1)
    get.return_value = description

    assert attributeset.get_statistics_bucket('__mock__') == bucket


@pytest.mark.django_db
def test_attribute_set_get_completeness_empty():
    attributeset = AttributeSet(data={})
    completed, total = attributeset.get_completeness()
    assert completed == 0


def test_attribute_set_get_completeness_empty_value(attribute_description):
    attributeset = AttributeSet()
    attributeset.data = {
        attribute_description.json_key: None,
    }
    completed, total = attributeset.get_completeness()
    assert completed == 0


def test_attribute_set_get_completeness_non_empty(attribute_description):
    attributeset = AttributeSet()
    attributeset.data = {
        attribute_description.json_key: 1,
    }
    completed, total = attributeset.get_completeness()
    assert completed == 1


@pytest.mark.django_db
def test_attribute_description_by_category(attribute_descriptions):
    categories = AttributeDescription.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 4
    assert len(categories) == 1


@pytest.mark.django_db
def test_attribute_description_by_category_with_categories(
    attribute_descriptions, attribute_category
):
    description = AttributeDescription.objects.first()
    description.category = attribute_category
    description.save()

    categories = AttributeDescription.objects.by_category()
    assert len(categories[UNCATEGORIZED]) == 3
    assert len(categories) == 2


@pytest.mark.django_db
def test_attribute_description_by_category_with_qs(attribute_descriptions):
    qs = AttributeDescription.objects.filter(order__lte=1)

    categories = AttributeDescription.objects.by_category(qs=qs)
    assert len(categories[UNCATEGORIZED]) == 2
    assert len(categories) == 1


@pytest.mark.django_db
def test_last_contacted_elsewhere():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study)
    study_2 = mommy.make(Study)

    with freeze_time("2020-12-13 08:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        mommy.make(ParticipationRequestRevision, current=participationrequest_1)

    with freeze_time("2011-11-11 11:11"):
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)
        revision_2 = mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere == revision_2.created_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_several_others():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study)
    study_2 = mommy.make(Study)

    with freeze_time("2020-12-13 08:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        mommy.make(ParticipationRequestRevision, current=participationrequest_1)

    with freeze_time("2011-11-11 11:11"):
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    with freeze_time("2021-11-11 11:11"):
        participationrequest_3 = mommy.make(ParticipationRequest, study=study_2, subject=subject)
        revision_3 = mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_3,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere == revision_3.created_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_no_others():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study)

    with freeze_time("2020-12-13 08:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        mommy.make(ParticipationRequestRevision, current=participationrequest_1)

    with freeze_time("2011-11-11 11:11"):
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    with freeze_time("2021-11-11 11:11"):
        participationrequest_3 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_3,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere is None


@pytest.mark.django_db
def test_last_contacted_elsewhere_several_studies():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study)
    study_2 = mommy.make(Study)
    study_3 = mommy.make(Study)

    with freeze_time("2020-12-13 08:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        mommy.make(ParticipationRequestRevision, current=participationrequest_1)

    with freeze_time("2011-11-11 11:11"):
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    with freeze_time("2021-11-11 11:11"):
        participationrequest_3 = mommy.make(ParticipationRequest, study=study_3, subject=subject)
        revision_3 = mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_3,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere == revision_3.created_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_not_contacted():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study)
    study_2 = mommy.make(Study)

    with freeze_time("2020-12-13 08:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        mommy.make(ParticipationRequestRevision, current=participationrequest_1)

    with freeze_time("2011-11-11 11:11"):
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_CONTACTED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere is None
