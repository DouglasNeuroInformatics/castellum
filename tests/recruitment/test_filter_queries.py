import datetime

import pytest
from django.utils import timezone
from freezegun import freeze_time
from model_bakery import baker

from castellum.appointments.models import Appointment
from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.recruitment.models import ReliabilityEntry
from castellum.subjects.models import Consent
from castellum.subjects.models import Subject


def has_match(q):
    return Subject.objects.filter(q).exists()


def test_has_consent(subject):
    q = filter_queries.has_consent()
    assert not has_match(q)
    baker.make(Consent, subject=subject, _fill_optional=['document'])
    assert has_match(q)


def test_has_consent_include_waiting(db):
    with freeze_time('1990-01-01 12:00:00'):
        baker.make(Contact)
    with freeze_time('2000-01-01 12:00:00'):
        q = filter_queries.has_consent(include_waiting=True)
        assert not has_match(q)

        baker.make(Contact)
        assert has_match(q)


def test_has_consent_exclude_deprecated(subject):
    baker.make(
        Consent,
        subject=subject,
        _fill_optional=['document'],
        document__is_deprecated=True,
    )
    assert has_match(filter_queries.has_consent())
    assert not has_match(filter_queries.has_consent(exclude_deprecated=True))


def test_is_available(subject):
    with freeze_time('2000-01-02'):
        subject.not_available_until = timezone.now()
        subject.save()
    with freeze_time('2000-01-01'):
        assert not has_match(filter_queries.is_available())
    with freeze_time('2000-01-02'):
        assert has_match(filter_queries.is_available())
    with freeze_time('2000-01-03'):
        assert has_match(filter_queries.is_available())


@pytest.mark.parametrize('date', [
    '1990-01-01',
    '1991-01-01',
    '1992-01-01',
    pytest.param('1989-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1989-12-31', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1992-01-02', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1993-01-01', marks=pytest.mark.xfail(strict=True)),
])
def test_last_study_participation_created_at(db, date):
    with freeze_time(date):
        baker.make(Contact)
    assert has_match(filter_queries.last_study_participation(
        after=datetime.date(1990, 1, 1),
        before=datetime.date(1992, 1, 1),
    ))


@pytest.mark.parametrize('date', [
    '1990-01-01',
    '1991-01-01',
    '1992-01-01',
    pytest.param('1989-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1989-12-31', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1992-01-02', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1993-01-01', marks=pytest.mark.xfail(strict=True)),
])
def test_last_study_participation_participation(db, date):
    with freeze_time('1970-01-01'):
        contact = baker.make(Contact)
    with freeze_time(date):
        baker.make(
            Participation,
            subject=contact.subject,
            status=Participation.COMPLETED,
        )
    assert has_match(filter_queries.last_study_participation(
        after=datetime.date(1990, 1, 1),
        before=datetime.date(1992, 1, 1),
    ))


@pytest.mark.parametrize('date', [
    '1990-01-01',
    '1991-01-01',
    '1992-01-01',
    pytest.param('1989-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1989-12-31', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1992-01-02', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1993-01-01', marks=pytest.mark.xfail(strict=True)),
])
def test_last_study_participation_appointment(db, date):
    with freeze_time('1970-01-01'):
        participation = baker.make(Participation)
    with freeze_time(date):
        baker.make(
            Appointment,
            participation=participation,
            start=timezone.now(),
        )
    with freeze_time('2000-01-01'):
        assert has_match(filter_queries.last_study_participation(
            after=datetime.date(1990, 1, 1),
            before=datetime.date(1992, 1, 1),
        ))


def test_last_study_participation_ignore_participation(db):
    with freeze_time('1970-01-01'):
        participation = baker.make(Participation)
    with freeze_time('1991-01-01'):
        baker.make(
            Appointment,
            participation=participation,
            start=timezone.now(),
        )
    with freeze_time('1995-01-01'):
        baker.make(Participation, subject=participation.subject)
    with freeze_time('2000-01-01'):
        assert has_match(filter_queries.last_study_participation(
            after=datetime.date(1990, 1, 1),
            before=datetime.date(1992, 1, 1),
        ))
        assert not has_match(filter_queries.last_study_participation(
            after=datetime.date(1999, 1, 1),
            before=datetime.date(2001, 1, 1),
        ))


def test_reliability(subject, study):
    baker.make(ReliabilityEntry, subject=subject, was_reliable=False, _quantity=2)

    assert has_match(filter_queries.reliability(study))

    study.max_reliability_issues = 0
    assert not has_match(filter_queries.reliability(study))

    study.max_reliability_issues = 1
    assert not has_match(filter_queries.reliability(study))

    study.max_reliability_issues = 2
    assert has_match(filter_queries.reliability(study))
