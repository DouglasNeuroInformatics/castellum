import datetime

from django.conf import settings

import pytest

from castellum.utils import mail


def prepare_context(data):
    context = {
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'language': settings.LANGUAGE_CODE,
        'subject_prefix': '',
        'signature': '',
        'connection': {}
    }
    context.update(data)
    return context


@pytest.mark.unittest
def test_prepare_body_template():
    context = prepare_context({})
    body = ('Foo {{ bar }}', {'bar': 'baz'})
    assert mail.prepare_body(body, context) == 'Foo baz'


@pytest.mark.unittest
@pytest.mark.parametrize('lang,expected', [
    ('en', 'Jan. 1, 2000'),
    ('de', '1. Januar 2000'),
])
def test_prepare_body_language(lang, expected):
    dt = datetime.datetime(2000, 1, 1, 13, 0, 0)
    body = ('{{ dt|date }}', {'dt': dt})
    context = prepare_context({'language': lang})
    assert mail.prepare_body(body, context) == expected
