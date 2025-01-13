# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone

from .models import AuditEvent


def cleanup(dt=relativedelta(years=1)):
    threshold = timezone.now() - dt
    AuditEvent.objects.filter(created_at__lt=threshold).delete()


def audit(action, username, *, study_pk=None, subject_pk=None, extra=None):
    if settings.CASTELLUM_AUDIT_TRAIL_ENABLED:
        cleanup()
        AuditEvent.objects.create(
            action=action,
            username=username or 'anon',
            study_pk=study_pk,
            subject_pk=subject_pk,
            extra=extra,
        )
