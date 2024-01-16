# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.shortcuts import get_object_or_404

from castellum.appointments.mixins import BaseAppointmentFeed
from castellum.castellum_auth.mixins import ParamAuthMixin
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Resource
from castellum.studies.models import Study

from .mixins import BaseFollowUpFeed
from .models import Participation


class FollowUpFeedForStudy(
    ParamAuthMixin, StudyMixin, PermissionRequiredMixin, BaseFollowUpFeed
):
    permission_required = 'recruitment.recruit'
    study_status = [Study.EXECUTION]

    def items(self):
        return (
            Participation.objects
            .filter(study=self.study, followup_date__isnull=False)
            .order_by('-followup_date', '-followup_time')
        )


class FollowUpFeedForUser(ParamAuthMixin, BaseFollowUpFeed):
    def items(self):
        perms = ['recruitment.recruit', 'studies.access_study']
        for study in Study.objects.filter(status=Study.EXECUTION):
            if not self.request.user.has_perms(perms, obj=study):
                continue
            yield from (
                Participation.objects
                .filter(study=study, followup_date__isnull=False)
                .order_by('-followup_date', '-followup_time')
            )


class AppointmentFeedForStudy(
    ParamAuthMixin, StudyMixin, PermissionRequiredMixin, BaseAppointmentFeed
):
    permission_required = ['studies.access_study']
    study_status = [Study.EXECUTION]

    def has_permission(self):
        if not super().has_permission():
            return False
        return any(self.request.user.has_perm(perm, obj=self.study) for perm in [
            'appointments.change_appointment',
            'recruitment.conduct_study',
        ])

    def items(self):
        return super().items().filter(session__study=self.study)

    def item_title(self, item):
        return ''


class AppointmentFeedForResource(ParamAuthMixin, BaseAppointmentFeed):
    def items(self):
        resource = get_object_or_404(Resource, pk=self.kwargs['pk'])
        return (
            super().items()
            .filter(session__resources=resource)
            .exclude(session__study__status=Study.FINISHED)
        )

    def item_title(self, item):
        return item.session.study.name
