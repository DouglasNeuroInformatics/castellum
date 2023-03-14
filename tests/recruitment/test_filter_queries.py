from freezegun import freeze_time
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
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
