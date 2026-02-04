# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from castellum.appointments.models import Appointment
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.models import Resource

from .helpers import get_external_resource_events
from .mixins import BaseCalendarView


class ReceptionView(PermissionRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/reception.html'
    permission_required = 'appointments.view_current_appointments'

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(start__date=datetime.date.today())
            .order_by('start')
            .select_related(
                'participation__subject',
                'participation__study',
                'session',
            )
            .prefetch_related(
                'assigned_conductors',
            )
        )


class ResourceListView(LoginRequiredMixin, ListView):
    model = Resource
    template_name = 'appointments/resource_list.html'


class ResourceDetailView(LoginRequiredMixin, BaseCalendarView):
    model = Resource
    base_template = 'appointments/resource_base.html'

    def get_queryset(self):
        return super().get_queryset().filter(managers=self.request.user)

    def get_appointments(self):
        return (
            super()
            .get_appointments()
            .filter(session__resources=self.object)
            .select_related('participation__subject', 'participation__study', 'session')
        )

    def render_appointment(self, appointment):
        if self.request.user.has_privacy_level(
            appointment.participation.subject.privacy_level
        ):
            name = appointment.participation.subject.contact.full_name
        else:
            name = _('(insufficient privacy level)')

        associated_study = appointment.participation.study
        associated_session_name = appointment.session.name
        return {
            'title': f'{name} ({associated_study} - {associated_session_name})',
            'url': reverse('execution:participation-detail', args=[
                appointment.participation.study.pk,
                appointment.participation.pk,
            ]),
            **super().render_appointment(appointment),
        }

    def get_events(self):
        start = datetime.datetime.fromisoformat(self.request.GET['start'])
        end = datetime.datetime.fromisoformat(self.request.GET['end'])
        return super().get_events() + get_external_resource_events(
            self.object, start, end
        )
