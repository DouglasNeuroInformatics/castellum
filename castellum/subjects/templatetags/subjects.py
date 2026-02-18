# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import quote
from urllib.parse import unquote

from django import template
from django.conf import settings
from django.urls import reverse

from castellum.utils.mail import MailContext

register = template.Library()


def build_uri(context, participation, subject, body, body_en):
    ctx = MailContext('internal')

    def get_mail_data():
        url = reverse('execution:participation-pseudonyms', args=[
            participation.study.pk, participation.pk
        ])
        return {
            'study': participation.study,
            'url': context['request'].build_absolute_uri(url),
            'name': participation.study.contact_person,
            'sender_name': context['user'].get_full_name(),
        }

    subject = subject.format(**get_mail_data())
    body = ctx.prepare_body((get_mail_data, body, body_en))

    return (
        f'mailto:{participation.study.email}'
        f'?subject={quote(subject, safe=[])}&body={quote(body, safe=[])}'
    )


@register.simple_tag(takes_context=True)
def delete_mail_uri(context, participation):
    return build_uri(
        context,
        participation,
        settings.CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_SUBJECT,
        settings.CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_BODY,
        settings.CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_BODY_EN,
    )


@register.simple_tag(takes_context=True)
def export_mail_uri(context, participation):
    return build_uri(
        context,
        participation,
        settings.CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_SUBJECT,
        settings.CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_BODY,
        settings.CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_BODY_EN,
    )


@register.simple_tag(takes_context=True)
def subject_media_url(context, url):
    """Convert internal to public media URL.

    Uploaded files for subjects have 4 different URLs:

    -   The internal URL, e.g. /media/subjects/some/path.pdf
    -   3 public URLs, e.g.:
        -   /media/subjects/<uuid>/some/path.pdf
        -   /media/execution/<study_id>/<id>/some/path.pdf
        -   /media/recruitment/<study_id>/<id>/some/path.pdf

    This template tag converts the internal URL to an external one.
    It relies on ``view.get_subject_media_url(path)`` to pick one of the
    three options.

    The public URLs point to subclasses of
    ``castellum.utils.views.ProtectedMediaView`` that do all relevant
    security checks and then convert the URL back to an internal URL to
    deliver the actual media file.
    """
    url_prefix = f'/{settings.MEDIA_URL.strip("/")}/subjects/{context["subject"].pk}/'
    if not url.startswith(url_prefix):
        raise ValueError(url)
    path = unquote(url.removeprefix(url_prefix))
    return context['view'].get_subject_media_url(path)
