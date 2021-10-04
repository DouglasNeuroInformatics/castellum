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
from django.contrib import messages
from django.urls import reverse
from django.utils import formats
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment.mixins import ParticipationMixin
from castellum.recruitment.models import Participation
from castellum.utils import add_working_days
from castellum.utils.feeds import BaseCalendarFeed
from castellum.utils.mail import MailContext

from .forms import AppointmentsForm
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

    def format_datetime(dt):
        if not dt:
            return _('not scheduled')
        return formats.date_format(timezone.localtime(dt), 'DATETIME_FORMAT')

    def get_mail_data():
        return {
            'study': participation.study,
            'changes': '\n'.join('{} -> {}'.format(
                format_datetime(old),
                format_datetime(new),
            ) for (old, new) in relevant_changes),
            'participation_url': request.build_absolute_uri(reverse(
                'execution:participation-detail',
                args=[participation.study.pk, participation.pk]
            )),
            'calendar_url': request.build_absolute_uri(reverse(
                'execution:calendar',
                args=[participation.study.pk]
            )),
        }

    recipients = [user.email for user in participation.study.conductors if user != request.user]
    if recipients:
        with MailContext('internal') as ctx:
            return ctx.send_mail(
                settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_SUBJECT,
                (
                    get_mail_data,
                    settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY,
                    settings.CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY_EN,
                ),
                recipients,
                cc=[request.user.email],
            )


class BaseAppointmentsUpdateView(ParticipationMixin, PermissionRequiredMixin, UpdateView):
    model = Participation
    form_class = AppointmentsForm
    template_name = 'appointments/appointments_form.html'
    permission_required = 'appointments.change_appointment'

    def get_object(self, queryset=None):
        return self.participation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reminder_period'] = settings.CASTELLUM_APPOINTMENT_REMINDER_PERIOD.days
        return context

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        response = super().form_valid(form)
        send_appointment_notifications(self.request, self.object, form.appointment_changes)
        messages.success(self.request, _('Data has been saved.'))
        return response


class BaseAppointmentFeed(BaseCalendarFeed):
    def items(self):
        qs = Appointment.objects.filter(participation__status=Participation.INVITED)
        filters = self.get_filters()
        if 'start' in filters:
            qs = qs.filter(start__gte=filters['start'])
        if 'end' in filters:
            qs = qs.filter(start__lte=filters['end'])
        return qs

    def item_start(self, item):
        return item.start

    def item_end(self, item):
        return item.end
