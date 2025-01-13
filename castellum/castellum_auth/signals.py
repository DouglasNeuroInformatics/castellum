# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from django.utils.translation import gettext_noop

from .middlewares import set_last_active

monitoring_logger = logging.getLogger('monitoring.auth')


def set_last_active_on_login(sender, user, request, **kwargs):
    set_last_active(request)


def log_login(sender, user, request, **kwargs):
    from castellum.audit.helpers import audit
    monitoring_logger.info(f'Login by {user.pk}')
    audit(gettext_noop('login'), user.username)


def log_failed_login(sender, credentials, request, **kwargs):
    from castellum.audit.helpers import audit
    monitoring_logger.info(
        f'Failed login with username "{credentials.get("username")}"'
    )
    audit(gettext_noop('login failed'), credentials.get('username'))


def log_logout(sender, user, request, **kwargs):
    from castellum.audit.helpers import audit
    if user:
        monitoring_logger.info(f'Logout by {user.pk}')
        audit(gettext_noop('logout'), user.username)
