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
