# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings

import castellum


def get_settings(request):
    return {
        'CASTELLUM_VERSION': castellum.__version__,
        'CASTELLUM_SITE_TITLE': settings.CASTELLUM_SITE_TITLE,
        'CASTELLUM_SITE_LOGO': settings.CASTELLUM_SITE_LOGO,
        'BOOTSTRAP_THEME_COLORS': settings.BOOTSTRAP_THEME_COLORS,
        'CASTELLUM_DOCUMENTATION_LINK': settings.CASTELLUM_DOCUMENTATION_LINK,
        'CASTELLUM_LOGOUT_TIMEOUT': settings.CASTELLUM_LOGOUT_TIMEOUT,
        'CASTELLUM_ENABLE_STUDY_METADATA': settings.CASTELLUM_ENABLE_STUDY_METADATA,
        'CASTELLUM_GENERAL_RECRUITMENT_TEXT': (
            settings.CASTELLUM_GENERAL_RECRUITMENT_TEXT
        ),
        'CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED': (
            settings.CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED
        ),
        'CASTELLUM_REPORT_NOTIFICATION_TO': settings.CASTELLUM_REPORT_NOTIFICATION_TO,
        'CASTELLUM_REPORT_TEXT': settings.CASTELLUM_REPORT_TEXT,
        'CASTELLUM_AUDIT_TRAIL_ENABLED': settings.CASTELLUM_AUDIT_TRAIL_ENABLED,
        'SCHEDULER_URL': settings.SCHEDULER_URL,

        # Error templates do not get a context. Invert this value to
        # avoid demo warnings in that case.
        'DEMO': not settings.PRODUCTION,
    }
