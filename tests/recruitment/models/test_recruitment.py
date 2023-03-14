import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.models import Domain
from castellum.pseudonyms.models import Pseudonym
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.subjects.models import Subject


@pytest.mark.django_db
def test_last_contacted_elsewhere():
    subject = baker.make(Subject)
    study_1 = baker.make(Study)
    study_2 = baker.make(Study)

    with freeze_time('1970-01-01 12:00'):
        participation_1 = baker.make(Participation, study=study_1, subject=subject)
        participation_2 = baker.make(Participation, study=study_2, subject=subject)

    with freeze_time('2011-11-11 11:11'):
        participation_2.status = Participation.NOT_REACHED
        participation_2.save()

    participation_1 = Participation.objects.with_sort_properties().get(
        pk=participation_1.pk
    )
    assert participation_1.last_contacted_elsewhere == participation_2.updated_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_several_others():
    subject = baker.make(Subject)
    study_1 = baker.make(Study)
    study_2 = baker.make(Study)

    with freeze_time('1970-01-01 12:00'):
        participation_1 = baker.make(Participation, study=study_1, subject=subject)
        participation_2 = baker.make(Participation, study=study_2, subject=subject)

    with freeze_time('2020-12-13 08:00'):
        participation_1.save()

    with freeze_time('2011-11-11 11:11'):
        participation_2.status = Participation.NOT_REACHED
        participation_2.save()

    with freeze_time('2021-11-11 11:11'):
        participation_2.save()

    participation_1 = Participation.objects.with_sort_properties().get(
        pk=participation_1.pk
    )
    assert participation_1.last_contacted_elsewhere == participation_2.updated_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_no_others():
    subject = baker.make(Subject)
    study_1 = baker.make(Study)

    with freeze_time('1970-01-01 12:00'):
        participation_1 = baker.make(Participation, study=study_1, subject=subject)

    with freeze_time('2011-11-11 11:11'):
        participation_1.status = Participation.NOT_REACHED
        participation_1.save()

    with freeze_time('2021-11-11 11:11'):
        participation_1.save()

    participation_1 = Participation.objects.with_sort_properties().get(
        pk=participation_1.pk
    )
    assert participation_1.last_contacted_elsewhere is None


@pytest.mark.django_db
def test_last_contacted_elsewhere_several_studies():
    subject = baker.make(Subject)
    study_1 = baker.make(Study)
    study_2 = baker.make(Study)
    study_3 = baker.make(Study)

    with freeze_time('1970-01-01 12:00'):
        participation_1 = baker.make(Participation, study=study_1, subject=subject)
        participation_2 = baker.make(Participation, study=study_2, subject=subject)
        participation_3 = baker.make(Participation, study=study_3, subject=subject)

    with freeze_time('2011-11-11 11:11'):
        participation_2.status = Participation.NOT_REACHED
        participation_2.save()

    with freeze_time('2021-11-11 11:11'):
        participation_3.status = Participation.NOT_REACHED
        participation_3.save()

    participation_1 = Participation.objects.with_sort_properties().get(
        pk=participation_1.pk
    )
    assert participation_1.last_contacted_elsewhere == participation_3.updated_at


@pytest.mark.django_db
def test_last_contacted_elsewhere_not_contacted():
    subject = baker.make(Subject)
    study_1 = baker.make(Study)
    study_2 = baker.make(Study)

    with freeze_time('1970-01-01 12:00'):
        participation_1 = baker.make(Participation, study=study_1, subject=subject)
        participation_2 = baker.make(Participation, study=study_2, subject=subject)

    with freeze_time('2011-11-11 11:11'):
        participation_2.status = Participation.NOT_CONTACTED
        participation_2.save()

    participation_1 = Participation.objects.with_sort_properties().get(
        pk=participation_1.pk
    )
    assert participation_1.last_contacted_elsewhere is None


@pytest.mark.django_db
def test_attempts():
    with freeze_time('1970-01-01 12:00'):
        participation = baker.make(Participation, status=Participation.NOT_REACHED)

    with freeze_time('1970-01-02 12:00'):
        participation.status = Participation.INVITED
        participation.save()

    with freeze_time('1970-01-03 12:00'):
        participation.status = Participation.NOT_REACHED
        participation.save()

    with freeze_time('1970-01-04 12:00'):
        participation.status = Participation.NOT_REACHED
        participation.save()

    participation = Participation.objects.with_sort_properties().get(
        pk=participation.pk
    )
    assert participation.attempts == 2


@pytest.mark.django_db
def test_attempts_single_revision():
    participation = baker.make(Participation, status=Participation.AWAITING_RESPONSE)
    participation = Participation.objects.with_sort_properties().get(
        pk=participation.pk
    )
    assert participation.attempts == 1


@pytest.mark.django_db
def test_assigned_to_me(user):
    participation = baker.make(Participation, assigned_recruiter__user=user)
    participation = Participation.objects.with_assigned_to_me(user).get(
        pk=participation.pk
    )
    assert participation.assigned_to_me == 1


@pytest.mark.django_db
def test_participation_create_delete_pseudonym():
    start_count = Pseudonym.objects.count()
    study = baker.make(Study)

    participation = baker.make(Participation, study=study)

    # create pseudonym
    domain = baker.make(Domain, context=study)
    get_pseudonym(participation.subject, domain.key)

    assert Pseudonym.objects.count() == start_count + 1

    participation.study.delete()
    assert Pseudonym.objects.count() == start_count
