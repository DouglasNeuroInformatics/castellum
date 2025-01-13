# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.signals import user_login_failed

from . import signals


class CastellumAuthConfig(AppConfig):
    name = 'castellum.castellum_auth'

    def ready(self):
        user_logged_in.connect(signals.set_last_active_on_login)
        user_logged_in.connect(signals.log_login)
        user_logged_out.connect(signals.log_logout)
        user_login_failed.connect(signals.log_failed_login)
