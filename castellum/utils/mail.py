# (c) 2018-2020
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


def get_context(name=None):
    context = {
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'language': settings.LANGUAGE_CODE,
        'subject_prefix': '',
        'signature': '',
        'connection': {}
    }
    if name:
        context.update(settings.CASTELLUM_MAIL[name])
    return context


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


def prepare_body(body, context):
    if not isinstance(body, str):
        body = render_body_with_fallback(*body, lang=context['language'])
    body += context['signature']
    return body


def send_mass_mail(datatuples, context=None):
    context = get_context(context)
    connection = get_connection(**context['connection'])
    messages = [
        EmailMessage(
            subject=context['subject_prefix'] + subject,
            body=prepare_body(body, context),
            from_email=context['from_email'],
            to=recipients,
            connection=connection,
            **kwargs,
        )
        for subject, body, recipients, kwargs in datatuples
    ]
    return connection.send_messages(messages)


def send_mail(subject, body, recipients, context=None, **kwargs):
    return send_mass_mail([(subject, body, recipients, kwargs)], context)
