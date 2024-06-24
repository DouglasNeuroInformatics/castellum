import datetime

import pytest
from django.core import mail
from django.utils.formats import date_format

from castellum.utils.mail import MailContext
from castellum.utils.mail import render_body_with_fallback


def get_mail_data():
    return {
        'date': date_format(datetime.date(2000, 1, 1))
    }


@pytest.mark.unittest
def test_render_body_with_fallback():
    assert render_body_with_fallback(get_mail_data, 'DE {date}', 'EN {date}', 'de') == (
        '++++ FOR INFORMATION IN ENGLISH SEE BELOW ++++\n'
        '\n'
        '\n'
        'DE 1. Januar 2000\n'
        '\n'
        '\n'
        '++++ INFORMATION IN ENGLISH ++++\n'
        '\n'
        '\n'
        'EN Jan. 1, 2000'
    )


def test_mail_body(mailoutbox):
    with MailContext() as ctx:
        ctx.send_mail('subject', 'body', ['test@example.com'])

    assert mail.outbox[0].extra_headers.get('Auto-Submitted') == 'auto-generated'
