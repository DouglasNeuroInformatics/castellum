import pytest
from freezegun import freeze_time
from model_mommy import mommy

from castellum.recruitment.models import ParticipationRequest
from castellum.recruitment.models import ParticipationRequestRevision
from castellum.studies.models import Study
from castellum.subjects.models import Subject


@pytest.mark.django_db
def test_last_contacted_elsewhere():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study, domain=None)
    study_2 = mommy.make(Study, domain=None)

    with freeze_time("1970-01-01 12:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)

    with freeze_time("2011-11-11 11:11"):
        revision = mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere == revision.created_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_several_others():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study, domain=None)
    study_2 = mommy.make(Study, domain=None)

    with freeze_time("1970-01-01 12:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)

    with freeze_time("2020-12-13 08:00"):
        mommy.make(ParticipationRequestRevision, current=participationrequest_1)

    with freeze_time("2011-11-11 11:11"):
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    with freeze_time("2021-11-11 11:11"):
        revision = mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere == revision.created_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_no_others():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study, domain=None)

    with freeze_time("1970-01-01 12:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)

    with freeze_time("2011-11-11 11:11"):
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_1,
            status=ParticipationRequest.NOT_REACHED,
        )

    with freeze_time("2021-11-11 11:11"):
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_1,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere is None


@pytest.mark.django_db
def test_last_contacted_elsewhere_several_studies():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study, domain=None)
    study_2 = mommy.make(Study, domain=None)
    study_3 = mommy.make(Study, domain=None)

    with freeze_time("1970-01-01 12:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)
        participationrequest_3 = mommy.make(ParticipationRequest, study=study_3, subject=subject)

    with freeze_time("2011-11-11 11:11"):
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_REACHED,
        )

    with freeze_time("2021-11-11 11:11"):
        revision = mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_3,
            status=ParticipationRequest.NOT_REACHED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere == revision.created_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_not_contacted():
    subject = mommy.make(Subject)
    study_1 = mommy.make(Study, domain=None)
    study_2 = mommy.make(Study, domain=None)

    with freeze_time("1970-01-01 12:00"):
        participationrequest_1 = mommy.make(ParticipationRequest, study=study_1, subject=subject)
        participationrequest_2 = mommy.make(ParticipationRequest, study=study_2, subject=subject)

    with freeze_time("2011-11-11 11:11"):
        mommy.make(
            ParticipationRequestRevision,
            current=participationrequest_2,
            status=ParticipationRequest.NOT_CONTACTED,
        )

    participationrequest_1 = ParticipationRequest.objects.get(pk=participationrequest_1.pk)
    assert participationrequest_1.last_contacted_elsewhere is None
