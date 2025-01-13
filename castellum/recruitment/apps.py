# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete

from . import signals


class RecruitmentConfig(AppConfig):
    name = 'castellum.recruitment'

    def ready(self):
        pre_delete.connect(signals.delete_attribute_data)
        post_save.connect(signals.sync_date_of_birth)
