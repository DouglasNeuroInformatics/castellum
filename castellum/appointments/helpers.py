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
from django.utils import formats


def date_format(date):
    return formats.date_format(date, 'l, ') + formats.date_format(date, 'DATETIME_FORMAT')


def get_reminder_body(name, session, date):
    def get_mail_data():
        return {
            'name': name,
            'study': session.study.name,
            'date': date_format(date),
            'reply_to': session.study.email,
            'session_reminder_text': session.reminder_text.strip() or '—',
        }

    return (
        get_mail_data,
        settings.CASTELLUM_APPOINTMENT_MAIL_BODY,
        settings.CASTELLUM_APPOINTMENT_MAIL_BODY_EN,
    )
