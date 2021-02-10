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

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse

from castellum.appointments.mixins import BaseAppointmentFeed
from castellum.studies.models import Study


class BaseExecutionAppointmentFeed(BaseAppointmentFeed):
    def item_title(self, item):
        return f'{item.participation.subject.contact.full_name} - {item.session.name}'

    def item_link(self, item):
        return reverse('execution:participation-detail', args=[
            item.session.study.pk, item.participation.pk
        ])

    def item_description(self, item):
        return self.request.build_absolute_uri(self.item_link(item))


class AppointmentFeedForStudy(BaseExecutionAppointmentFeed):
    def get_object(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=kwargs['pk'], status=Study.EXECUTION)
        perms = ['recruitment.conduct_study', 'studies.access_study']
        if not self.request.user.has_perms(perms, obj=study):
            raise PermissionDenied
        return study

    def items(self, study):
        return super().items(study)\
            .filter(session__study=study)\
            .select_related('participation__subject', 'session__study')


class AppointmentFeedForUser(BaseExecutionAppointmentFeed):
    def get_object(self, request, *args, **kwargs):
        return self.request.user

    def items(self, user):
        items = super().items(user)\
            .filter(session__study__status=Study.EXECUTION)\
            .select_related('participation__subject', 'session__study')

        perms = ['recruitment.conduct_study', 'studies.access_study']
        for item in items:
            if user.has_perms(perms, obj=item.session.study):
                yield item
