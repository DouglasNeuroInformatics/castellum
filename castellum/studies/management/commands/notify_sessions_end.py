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

import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from castellum.studies.models import Study
from castellum.utils.mail import MailContext


class Command(BaseCommand):
    help = 'Notify study members on the end of sessions'

    def handle(self, *args, **options):
        with MailContext('internal') as ctx:
            for study in Study.objects.filter(sessions_end=datetime.date.today()):
                ctx.send_mail(
                    settings.CASTELLUM_SESSIONS_END_MAIL_SUBJECT.format(study=study),
                    (
                        lambda: {'study': study},
                        settings.CASTELLUM_SESSIONS_END_MAIL_BODY,
                        settings.CASTELLUM_SESSIONS_END_MAIL_BODY_EN,
                    ),
                    [user.email for user in study.members.all() if (
                        user.has_perm('recruitment.conduct_study', obj=study)
                        or user.has_perm('studies.change_study', obj=study)
                    )],
                )
