# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

from urllib.parse import quote

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

    return 'mailto:{}?subject={}&body={}'.format(
        participation.study.email,
        quote(subject, safe=[]),
        quote(body, safe=[]),
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
    security checks and then convert the URL back an internal URL to
    deliver the actual media file.
    """
    url_prefix = '/{}/subjects/'.format(settings.MEDIA_URL.strip('/'))
    if not url.startswith(url_prefix):
        raise TypeError(url)
    return context['view'].get_subject_media_url(url[len(url_prefix):])


@register.filter
def privacy_level(subject):
    if subject.privacy_level > 1:
        return 'danger'
    elif subject.privacy_level > 0:
        return 'warning'
    else:
        return 'body'
