# (c) 2018-2021
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

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
    def __init__(self, name=None):
        self.connection = None
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
            try:
                self.connection.open()
            except Exception:
                self.connection.close()
                self.connection = None
                raise
        return self

    def __exit__(self, type, value, traceback):
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
        return msg.send(fail_silently=True)

    def send_separate_mails(self, subject, body, recipients, **kwargs):
        count = 0
        for recipient in recipients:
            count += self.send_mail(subject, body, [recipient], **kwargs)
        return count
