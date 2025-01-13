# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.utils import translation


def render_body_with_fallback(get_mail_data, text, fallback=None, lang=None):
    """Render text and english fallback text in the correct locale context."""

    with translation.override(lang):
        s = text.format(**get_mail_data())

    if lang != settings.CASTELLUM_FALLBACK_LANGUAGE and fallback:
        before, after = settings.CASTELLUM_FALLBACK_LANGUAGE_MARKERS
        with translation.override(settings.CASTELLUM_FALLBACK_LANGUAGE):
            s_fallback = fallback.format(**get_mail_data())
        s = '\n\n\n'.join([before, s, after, s_fallback])

    return s


class MailContext:
    def __init__(self, name=None, connection=None):
        self.connection = connection
        self.close_connection = False
        self.data = {
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'language': settings.LANGUAGE_CODE,
            'subject_prefix': '',
            'recipients_text': '',
            'signature': '',
            'connection': {},
        }
        if name:
            self.data.update(settings.CASTELLUM_MAIL[name])

    def __enter__(self):
        if not self.connection:
            self.connection = get_connection(**self.data['connection'])
            self.close_connection = True
            try:
                self.connection.open()
            except Exception:
                self.connection.close()
                self.connection = None
                raise
        return self

    def __exit__(self, type, value, traceback):
        if self.close_connection:
            self.connection.close()
        self.connection = None

    def prepare_body(self, body, recipients_string=''):
        if not isinstance(body, str):
            body = render_body_with_fallback(*body, lang=self.data['language'])

        if recipients_string:
            body += self.data['recipients_text'].format(recipients_string)

        body += self.data['signature']
        return body

    def send_mail(self, subject, body, recipients, recipients_string='', **kwargs):
        assert self.connection
        msg = EmailMessage(
            subject=self.data['subject_prefix'] + subject,
            body=self.prepare_body(body, recipients_string),
            from_email=self.data['from_email'],
            to=recipients,
            connection=self.connection,
            **kwargs,
        )
        msg.extra_headers.setdefault('Auto-Submitted', 'auto-generated')
        return msg.send(fail_silently=True)

    def send_separate_mails(self, subject, body, recipients, **kwargs):
        count = 0
        for recipient in recipients:
            count += self.send_mail(subject, body, [recipient], **kwargs)
        return count
