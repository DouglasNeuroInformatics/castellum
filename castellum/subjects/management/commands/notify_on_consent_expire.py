# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from castellum.subjects.models import Consent
from castellum.utils.mail import MailContext


class Command(BaseCommand):
    help = 'Notify staff about consents that will soon expire'

    def handle(self, *args, **options):
        if not settings.CASTELLUM_CONSENT_EXPIRE_AT_MAIL_TO:
            raise CommandError('CASTELLUM_CONSENT_EXPIRE_AT_MAIL_TO not set')

        now = timezone.now()
        threshold = now + settings.CASTELLUM_CONSENT_EXPIRE_AT_MAIL_BEFORE

        consents = Consent.objects.filter(
            expire_at_notified=False,
            updated_at__gte=(now - models.F('document__expire_after')),
            updated_at__lt=(threshold - models.F('document__expire_after')),
        )

        subject_urls = [
            urljoin(
                settings.CASTELLUM_EMAIL_BASE_URL,
                reverse('subjects:data-protection', args=[consent.subject_id]),
            )
            for consent in consents
        ]

        if subject_urls:
            with MailContext('internal') as ctx:
                success = ctx.send_mail(
                    settings.CASTELLUM_CONSENT_EXPIRE_AT_MAIL_SUBJECT,
                    settings.CASTELLUM_CONSENT_EXPIRE_AT_MAIL_BODY.format(
                        subject_urls='\n'.join(subject_urls)
                    ),
                    settings.CASTELLUM_CONSENT_EXPIRE_AT_MAIL_TO,
                )

            if success:
                consents.update(expire_at_notified=True)
