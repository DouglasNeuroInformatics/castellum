# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings


def delete_scheduler_appointments_on_delete(sender, instance, using, **kwargs):
    from castellum.pseudonyms.helpers import get_pseudonym
    from castellum.recruitment.models import Participation
    from castellum.utils import scheduler

    if sender is Participation and settings.SCHEDULER_URL:
        for session in instance.study.studysession_set.exclude(schedule_id=None):
            pseudonym = get_pseudonym(instance.subject, session.domain)
            scheduler.delete(session.schedule_id, pseudonym)


def delete_appointments_on_save(sender, instance, using, **kwargs):
    from castellum.recruitment.models import Participation

    from .models import Appointment

    if sender is Participation and instance.status not in Participation.INVITED_SET:
        # PERF: ignore if instance has not been saved to the database yet
        if not instance.pk:
            return

        delete_scheduler_appointments_on_delete(sender, instance, using, **kwargs)
        Appointment.objects.filter(participation=instance).delete()
