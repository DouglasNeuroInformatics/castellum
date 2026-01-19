# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save

from castellum.pseudonyms.helpers import get_pseudonym_if_exists
from castellum.recruitment.models import Participation
from castellum.utils import scheduler

from .models import Appointment


def delete_scheduler_appointments_on_delete(sender, instance, using, **kwargs):
    if settings.SCHEDULER_URL:
        for session in instance.study.studysession_set.exclude(schedule_id=None):
            pseudonym = get_pseudonym_if_exists(instance.subject, session.domain)
            if pseudonym:
                scheduler.delete(session.schedule_id, pseudonym)


def delete_appointments_on_save(sender, instance, using, **kwargs):
    if instance.status not in Participation.INVITED_SET:
        # PERF: ignore if instance has not been saved to the database yet
        if not instance.pk:
            return

        delete_scheduler_appointments_on_delete(sender, instance, using, **kwargs)
        Appointment.objects.filter(participation=instance).delete()


def register_signal_handlers():
    pre_delete.connect(delete_scheduler_appointments_on_delete, sender=Participation)
    pre_save.connect(delete_appointments_on_save, sender=Participation)
