# (c) 2018-2021
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

from django.conf import settings


def delete_scheduler_appointments_on_delete(sender, instance, using, **kwargs):
    from castellum.pseudonyms.helpers import get_pseudonym
    from castellum.recruitment.models import Participation
    from castellum.utils import scheduler

    from .models import Appointment

    if sender is Participation and settings.SCHEDULER_URL:
        for session in instance.study.studysession_set.exclude(schedule_id=None):
            pseudonym = get_pseudonym(instance.subject, session.domain)
            scheduler.delete(session.schedule_id, pseudonym)
        qs = (
            Appointment.objects
            .filter(participation=instance)
            .exclude(session__schedule_id=None)
        )
        qs.delete()


def delete_scheduler_appointments_on_save(sender, instance, using, **kwargs):
    from castellum.recruitment.models import Participation

    if sender is Participation and instance.status != Participation.PARTICIPATING:
        # PERF: ignore if instance has not been saved to the database yet
        if not instance.pk:
            return
        delete_scheduler_appointments_on_delete(sender, instance, using, **kwargs)
