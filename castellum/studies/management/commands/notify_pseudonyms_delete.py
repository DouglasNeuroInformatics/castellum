# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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

import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from castellum.studies.models import Study
from castellum.utils.mail import MailContext


class Command(BaseCommand):
    help = 'Notify study coordinators when pseudonym lists should be deleted.'

    def handle(self, *args, **options):
        today = datetime.date.today()
        with MailContext('internal') as ctx:
            for study in (
                Study.objects
                .filter(pseudonyms_delete_date=today)
                .exclude(domains=None)
            ):
                ctx.send_mail(
                    settings.CASTELLUM_PSEUDONYMS_DELETE_MAIL_SUBJECT.format(study=study),
                    (
                        lambda: {
                            'study': study,
                            'study_url': urljoin(
                                settings.CASTELLUM_EMAIL_BASE_URL,
                                reverse('studies:domains', args=[study.pk]),
                            ),
                        },
                        settings.CASTELLUM_PSEUDONYMS_DELETE_MAIL_BODY,
                        settings.CASTELLUM_PSEUDONYMS_DELETE_MAIL_BODY_EN,
                    ),
                    [
                        user.email for user in study.members.all()
                        if user.has_perm('studies.change_study', obj=study)
                    ],
                )
