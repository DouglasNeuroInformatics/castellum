import datetime

import pytest
from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
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


@pytest.mark.parametrize('date', [
    '1990-01-02',
    '1991-01-01',
    '1991-12-31',
    pytest.param('1989-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1990-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1992-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1993-01-01', marks=pytest.mark.xfail(strict=True)),
])
def test_study_activity_created_at(study, date):
    study.recruitment_active_after = datetime.date(1990, 1, 1)
    study.recruitment_active_before = datetime.date(1992, 1, 1)
    study.save()

    with freeze_time(date):
        baker.make(Contact)
    assert has_match(filter_queries.study_activity(study))


@pytest.mark.parametrize('date', [
    '1990-01-02',
    '1991-01-01',
    '1991-12-31',
    pytest.param('1989-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1990-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1992-01-01', marks=pytest.mark.xfail(strict=True)),
    pytest.param('1993-01-01', marks=pytest.mark.xfail(strict=True)),
])
def test_study_activity_participation(study, date):
    study.recruitment_active_after = datetime.date(1990, 1, 1)
    study.recruitment_active_before = datetime.date(1992, 1, 1)
    study.save()

    with freeze_time('1970-01-01'):
        contact = baker.make(Contact)
    with freeze_time(date):
        baker.make(
            Participation,
            subject=contact.subject,
            status=Participation.PARTICIPATING,
        )
    assert has_match(filter_queries.study_activity(study))
