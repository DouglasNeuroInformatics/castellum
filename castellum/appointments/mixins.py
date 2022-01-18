# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

import datetime
import logging

from django.conf import settings
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import UpdateView

import requests

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.recruitment.mixins import ParticipationMixin
from castellum.recruitment.models import Participation
from castellum.studies.models import Resource
from castellum.utils import scheduler
from castellum.utils.feeds import BaseCalendarFeed

from .forms import AppointmentsForm
from .helpers import fetch_scheduler_appointments
from .helpers import send_appointment_notifications
from .models import Appointment

logger = logging.getLogger(__name__)


class SchedulerFetchParticipationMixin:
    def fetch_scheduler_appointments(self):
        changes = []
        for session in self.study.studysession_set.exclude(schedule_id=None):
            pseudonym = get_pseudonym(self.subject, session.domain)
            try:
                start = scheduler.get(session.schedule_id, pseudonym)
            except requests.RequestException as e:
                logger.error('Fetching schedule for session {} failed: {}'.format(session.pk, e))
                continue

            changes += Appointment.change_start(session, self.participation, start)
        send_appointment_notifications(
            self.participation, changes, self.request.build_absolute_uri('/')
        )
        return len(changes)

    def get(self, request, *args, **kwargs):
        if settings.SCHEDULER_URL:
            count = self.fetch_scheduler_appointments()
            if count > 0:
                messages.info(self.request, _(
                    'Some appointments have been updated from the external schedule'
                ))
        return super().get(request, *args, **kwargs)


class SchedulerFetchStudyMixin:
    def get(self, request, *args, **kwargs):
        if settings.SCHEDULER_URL:
            base_url = request.build_absolute_uri('/')
            fetch_scheduler_appointments(self.study, base_url, timeout=300)
        return super().get(request, *args, **kwargs)


class BaseAppointmentsUpdateView(
    SchedulerFetchParticipationMixin, ParticipationMixin, PermissionRequiredMixin, UpdateView
):
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

    def has_participation_overlap(self):
        return any((
            self.object.appointment_set
            .annotate_end()
            .exclude(pk=appointment.pk)
            .filter(end__gt=appointment.start, start__lt=appointment.end)
            .exists()
        ) for appointment in self.object.appointment_set.all())

    def get_resource_overlaps(self):
        inner = (
            Appointment.objects
            .annotate_end()
            .exclude(pk=models.OuterRef('pk'))
            .filter(
                session__resources=models.OuterRef('session__resources'),
                participation__status=Participation.INVITED,
                end__gt=models.OuterRef('start'),
                start__lt=models.OuterRef('end'),
            )
        )
        outer = (
            self.object.appointment_set.all()
            .annotate_end()
            .alias(overlap=models.Subquery(inner.values('pk')[:1]))
            .exclude(overlap=None)
            .order_by()
        )
        return Resource.objects.filter(pk__in=outer.values('session__resources__pk'))

    def form_valid(self, form):
        response = super().form_valid(form)
        send_appointment_notifications(
            self.object,
            form.appointment_changes,
            self.request.build_absolute_uri('/'),
            user=self.request.user,
        )

        messages.success(self.request, _('Data has been saved.'))
        if self.has_participation_overlap():
            messages.warning(self.request, _('Some appointments overlap'))
        for resource in self.get_resource_overlaps():
            messages.warning(self.request, _(
                'Some appointments for {resource} overlap'
            ).format(resource=resource))
        return response


class BaseCalendarView(DetailView):
    template_name = 'appointments/calendar.html'

    @cached_property
    def filters(self):
        return {
            'start': datetime.datetime.fromisoformat(self.request.GET['start']),
            'end': datetime.datetime.fromisoformat(self.request.GET['end']),
        }

    def get_appointments(self):
        qs = Appointment.objects.filter(participation__status=Participation.INVITED)
        if 'start' in self.request.GET:
            qs = qs.annotate_end().filter(end__gte=self.filters['start'])
        if 'end' in self.request.GET:
            qs = qs.filter(start__lte=self.filters['end'])
        return qs

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


class BaseAppointmentFeed(BaseCalendarFeed):
    def items(self):
        return Appointment.objects.filter(participation__status=Participation.INVITED)

    def item_start(self, item):
        return item.start

    def item_end(self, item):
        return item.end

    def item_uid(self, item):
        return 'appointment-{}@{}'.format(item.pk, self.request.get_host())
