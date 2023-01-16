# (c) 2018-2023 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from castellum.studies.models import Resource

from .helpers import get_external_resource_events
from .mixins import BaseCalendarView


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
        if self.request.user.has_privacy_level(appointment.participation.subject.privacy_level):
            name = appointment.participation.subject.contact.full_name
        else:
            name = _('(insufficient privacy level)')
        return {
            'title': '{} ({} - {})'.format(
                name,
                appointment.participation.study,
                appointment.session.name,
            ),
            'url': reverse('execution:participation-detail', args=[
                appointment.participation.study.pk,
                appointment.participation.pk,
            ]),
            **super().render_appointment(appointment),
        }

    def get_events(self):
        start = datetime.datetime.fromisoformat(self.request.GET['start'])
        end = datetime.datetime.fromisoformat(self.request.GET['end'])
        return super().get_events() + get_external_resource_events(self.object, start, end)
