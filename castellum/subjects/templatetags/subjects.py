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
