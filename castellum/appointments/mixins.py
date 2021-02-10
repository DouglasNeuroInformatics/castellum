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
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView

from castellum.participations.models import Participation
from castellum.utils import add_working_days
from castellum.utils.feeds import BaseICalFeed
from castellum.utils.mail import MailContext

from .models import Appointment


def send_appointment_notifications(request, participation, changes):
    start = timezone.now()
    end = add_working_days(start, 2)
    relevant_changes = [
        (old, new) for (old, new) in changes if (
            (old and old >= start and old <= end) or
            (new and new >= start and new <= end)
        )
    ]

    if not relevant_changes:
        return

    body = settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY.format(
        study=participation.study,
        changes='\n'.join('{} -> {}'.format(
            timezone.localtime(old),
            timezone.localtime(new),
        ) for (old, new) in relevant_changes),
        participation_url=request.build_absolute_uri(reverse(
            'participations:participation-detail',
            args=[participation.study.pk, participation.pk]
        )),
        calendar_url=request.build_absolute_uri(reverse(
            'participations:calendar',
            args=[participation.study.pk]
        )),
    )

    with MailContext('internal') as ctx:
        return ctx.send_mail(
            settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_SUBJECT,
            body,
            [user.email for user in participation.study.conductors if user != request.user],
        )


class BaseCalendarView(DetailView):
    template_name = 'appointments/calendar.html'

    def get_appointments(self):
        return Appointment.objects.filter(participation__status=Participation.INVITED)

    def render_appointment(self, appointment):
        return {
            'start': appointment.start,
            'end': appointment.end,
        }

    def get_events(self):
        self.object = self.get_object()
        return [self.render_appointment(a) for a in self.get_appointments()]

    def get(self, request, *args, **kwargs):
        if 'events' in request.GET:
            return JsonResponse({'events': self.get_events()})
        else:
            return super().get(request, *args, **kwargs)


class BaseAppointmentFeed(BaseICalFeed):
    def items(self, obj):
        return Appointment.objects.filter(participation__status=Participation.INVITED)

    def item_start_datetime(self, item):
        return item.start

    def item_end_datetime(self, item):
        return item.end
