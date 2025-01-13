# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save

from . import signals


class AppointmentsConfig(AppConfig):
    name = 'castellum.appointments'

    def ready(self):
        pre_delete.connect(signals.delete_scheduler_appointments_on_delete)
        pre_save.connect(signals.delete_appointments_on_save)
