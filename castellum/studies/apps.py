# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete

from . import signals


class StudiesConfig(AppConfig):
    name = 'castellum.studies'

    def ready(self):
        pre_delete.connect(signals.delete_study_domain)

        post_save.connect(signals.create_session_domain)
        pre_delete.connect(signals.delete_session_domain)
