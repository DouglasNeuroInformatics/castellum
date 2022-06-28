from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment import filter_queries
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentDocument
from castellum.subjects.models import Subject


def has_match(q):
    return Subject.objects.filter(q).exists()


def test_has_consent(subject):
    q = filter_queries.has_consent()
    assert not has_match(q)
    document = baker.make(ConsentDocument)
    baker.make(Consent, subject=subject, document=document)
    assert has_match(q)


def test_has_consent_include_waiting(subject):
    q = filter_queries.has_consent(include_waiting=True)
    assert has_match(q)
    with freeze_time('2100-01-01 12:00:00'):
        q = filter_queries.has_consent(include_waiting=True)
        assert not has_match(q)


def test_has_consent_exclude_deprecated(subject):
    document = baker.make(ConsentDocument, is_deprecated=True)
    baker.make(Consent, subject=subject, document=document)
    assert has_match(filter_queries.has_consent())
    assert not has_match(filter_queries.has_consent(exclude_deprecated=True))
