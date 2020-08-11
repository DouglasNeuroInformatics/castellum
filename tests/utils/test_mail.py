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
def test_prepare_body_wrap():
    context = prepare_context({})
    body = (
        'The first line is short\n'
        'The second line is really long '
        'The second line is really long '
        'The second line is really long '
        'The second line is really long '
        'The second line is really long '
        'The second line is really long '
        'The second line is really long '
        '\n\n'
        'the end.'
    )
    assert mail.prepare_body(body, context) == (
        'The first line is short\n'
        'The second line is really long The second line is really long The second line\n'
        'is really long The second line is really long The second line is really long\n'
        'The second line is really long The second line is really long'
        '\n\n'
        'the end.'
    )
