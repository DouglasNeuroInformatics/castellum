# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.signals import user_login_failed
from django.utils.translation import gettext_noop

from castellum.audit.helpers import audit

from .middlewares import set_last_active


def set_last_active_on_login(sender, user, request, **kwargs):
    set_last_active(request)


def log_login(sender, user, request, **kwargs):
    audit(gettext_noop('login'), user.username)


def log_failed_login(sender, credentials, request, **kwargs):
    audit(gettext_noop('login failed'), credentials.get('username'))


def log_logout(sender, user, request, **kwargs):
    if user:
        audit(gettext_noop('logout'), user.username)


def register_signal_handlers():
    user_logged_in.connect(set_last_active_on_login)
    user_logged_in.connect(log_login)
    user_logged_out.connect(log_logout)
    user_login_failed.connect(log_failed_login)
