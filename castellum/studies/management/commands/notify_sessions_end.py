# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

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
                        lambda: {
                            'study': study,
                            'study_url': urljoin(
                                settings.CASTELLUM_EMAIL_BASE_URL,
                                reverse('studies:sessions', args=[study.pk]),
                            ),
                        },
                        settings.CASTELLUM_SESSIONS_END_MAIL_BODY,
                        settings.CASTELLUM_SESSIONS_END_MAIL_BODY_EN,
                    ),
                    [user.email for user in study.members.all() if (
                        user.has_perm('recruitment.conduct_study', obj=study)
                        or user.has_perm('studies.change_study', obj=study)
                    )],
                    cc=settings.CASTELLUM_STUDY_END_NOTIFICATION_CC,
                )
